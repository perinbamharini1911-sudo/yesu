import os
import shutil

import joblib
import pandas as pd
from sklearn.metrics import mean_absolute_error
from sklearn.preprocessing import LabelEncoder
from sklearn.tree import DecisionTreeRegressor

BASE = os.path.dirname(os.path.abspath(__file__))

# ==========================================
# LOAD DATASET (EXCEL)
# ==========================================

df = pd.read_excel(os.path.join(BASE, "library_borrowing.xlsx"))

print("Original Data:")
print(df.head())

# ==========================================
# ENCODE CATEGORY (string -> number)
# ==========================================

df["Category"] = df["Category"].astype(str).str.strip()

category_encoder = LabelEncoder()
df["Category_code"] = category_encoder.fit_transform(df["Category"])

print("\nCategories:", list(category_encoder.classes_))

# ==========================================
# HANDLE MISSING VALUES
# ==========================================

df = df.dropna(subset=["Year", "Month", "Category", "Borrow_Count"])

# ==========================================
# FEATURES & TARGET
# ==========================================

FEATURES = ["Category_code", "Year", "Month"]

X = df[FEATURES].values
y = df["Borrow_Count"].values

# ==========================================
# TEST ACCURACY  (train on old data, test on the LAST 12 MONTHS)
# ==========================================

t = df["Year"] * 12 + df["Month"]
test_mask = (t >= t.max() - 11).values

test_model = DecisionTreeRegressor(random_state=42)
test_model.fit(X[~test_mask], y[~test_mask])
y_pred = test_model.predict(X[test_mask])

mae = float(mean_absolute_error(y[test_mask], y_pred))
mape = float((abs(y[test_mask] - y_pred) / y[test_mask]).mean() * 100)

print("\nMean Absolute Error (last 12 months):", round(mae, 2))
print("Error percentage (MAPE):", round(mape, 2), "%")

# ==========================================
# FINAL MODEL (train on ALL data)
# ==========================================

model = DecisionTreeRegressor(random_state=42)
model.fit(X, y)

# ==========================================
# SAVE MODEL + ENCODERS
# ==========================================

encoders = {
    "category": category_encoder,
    "meta": {
        "mae": round(mae, 1),
        "mape": round(mape, 1),
        "first_year": int(df["Year"].min()),
        "last_year": int(df.loc[t.idxmax(), "Year"]),
        "last_month": int(df.loc[t.idxmax(), "Month"]),
    },
}

model_path = os.path.join(BASE, "demand_model.joblib")
enc_path = os.path.join(BASE, "demand_encoders.joblib")

joblib.dump(model, model_path)
joblib.dump(encoders, enc_path)

print("\n✅ Model Saved   : demand_model.joblib")
print("✅ Encoders Saved: demand_encoders.joblib")

# ==========================================
# COPY THE 2 FILES INTO THE DJANGO PROJECT
# ==========================================

project_dir = os.path.join(BASE, "..", "myproject")
if os.path.isfile(os.path.join(project_dir, "manage.py")):
    shutil.copy(model_path, project_dir)
    shutil.copy(enc_path, project_dir)
    print("✅ Both files copied to:", os.path.abspath(project_dir))
else:
    print("⚠ myproject folder not found. Copy the 2 .joblib files next to manage.py manually.")

# ==========================================
# SAMPLE PREDICTION
# ==========================================

sample = {"Category": "Computer Science", "Year": 2026, "Month": 1}

code = category_encoder.transform([sample["Category"]])[0]
prediction = model.predict([[code, sample["Year"], sample["Month"]]])

print("\nSample:", sample)
print("Predicted Borrows:", int(round(prediction[0])))
