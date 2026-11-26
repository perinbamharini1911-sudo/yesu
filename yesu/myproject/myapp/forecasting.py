"""Demand prediction using the trained Decision Tree model.

The model is trained by ml_training/train_model.py from the Excel file and saved as
two files that must sit next to manage.py:
    demand_model.joblib     - DecisionTreeRegressor
    demand_encoders.joblib  - LabelEncoder for Category (+ accuracy info)
"""
import os

from django.conf import settings

MODEL_PATH = os.path.join(settings.BASE_DIR, 'demand_model.joblib')
ENCODER_PATH = os.path.join(settings.BASE_DIR, 'demand_encoders.joblib')
MONTH_NAMES = ['January', 'February', 'March', 'April', 'May', 'June',
               'July', 'August', 'September', 'October', 'November', 'December']

_cache = {}


class ModelNotReady(Exception):
    """Raised when the model files are missing or cannot be loaded."""


def _load():
    if _cache:
        return _cache['model'], _cache['encoders']
    if not (os.path.isfile(MODEL_PATH) and os.path.isfile(ENCODER_PATH)):
        raise ModelNotReady(
            'Model files not found. Run ml_training/train_model.py and place '
            'demand_model.joblib and demand_encoders.joblib next to manage.py.')
    try:
        import joblib
        _cache['model'] = joblib.load(MODEL_PATH)
        _cache['encoders'] = joblib.load(ENCODER_PATH)
    except Exception as exc:  # missing library, blocked DLL, version mismatch ...
        raise ModelNotReady(f'Could not load the model files: {exc}')
    return _cache['model'], _cache['encoders']


def get_categories():
    _, encoders = _load()
    return [str(c) for c in encoders['category'].classes_]


def predict_demand(category, year, month):
    """Predict borrow demand of a category for a given year/month."""
    model, encoders = _load()
    meta = encoders['meta']

    if category not in get_categories():
        raise ValueError('Unknown category.')
    if year < meta['first_year']:
        raise ValueError(f"Year must be {meta['first_year']} or later.")

    code = int(encoders['category'].transform([category])[0])
    demand = max(0, int(round(float(model.predict([[code, year, month]])[0]))))

    is_actual = (year, month) <= (meta['last_year'], meta['last_month'])
    return {
        'category': category, 'year': year, 'month': month,
        'month_name': MONTH_NAMES[month - 1],
        'demand': demand, 'is_actual': is_actual,
        'mape': meta['mape'], 'mae': meta['mae'],
    }
