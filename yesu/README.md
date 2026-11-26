# Intelligent Library System with Demand Forecasting Module

Django project: login / register, home page, and a demand prediction form
(category, month, year, copies available -> predicted borrowing demand + restock advice).

## Step 1 - Train the model (ml_training folder)
    cd ml_training
    pip install -r requirements.txt
    python train_model.py
This reads library_borrowing.xlsx (Year, Month, Category, Borrow_Count), trains a
DecisionTreeRegressor and creates demand_model.joblib + demand_encoders.joblib.
The script copies both files into myproject (next to manage.py).

## Step 2 - Run the website
    cd myproject
    pip install -r requirements.txt
    python manage.py migrate
    python manage.py runserver
