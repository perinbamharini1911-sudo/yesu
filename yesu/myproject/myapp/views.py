import math

from django.contrib.auth import authenticate, get_user_model, login, logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render

from .forecasting import MONTH_NAMES, ModelNotReady, get_categories, predict_demand

User = get_user_model()

LOANS_PER_COPY_PER_MONTH = 2  # 14-day loan period -> about 2 loans per copy each month


# ------------------------------------------------------------------ auth
def login_f(request):
    tes = 'Welcome to the Library Login'

    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '').strip()
        user_check = authenticate(request, username=username, password=password)

        if user_check is not None:
            login(request, user_check)
            return redirect('homepage')

        return render(request, 'log.html',
                      {'tes': tes, 'error_message': 'Invalid username or password'})

    return render(request, 'log.html', {'tes': tes})


def register(request):
    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '')
        if not username or not password:
            return render(request, 'reg.html', {'error_message': 'Username and password are required'})
        if User.objects.filter(username=username).exists():
            return render(request, 'reg.html', {'error_message': 'Username already exists'})
        user_val = User(username=username)
        user_val.set_password(password)
        user_val.save()
        return redirect('login_f')
    return render(request, 'reg.html')


def logout_user(request):
    logout(request)
    return redirect('login_f')


# ------------------------------------------------------------- home page
@login_required(login_url='login_f')
def homepage(request):
    return render(request, 'hom.html')


# ------------------------------------------------- demand prediction form
@login_required(login_url='login_f')
def predict_page(request):
    context = {
        'categories': [],
        'months': list(enumerate(MONTH_NAMES, start=1)),
        'form': {'year': 2026, 'month': 1, 'copies': 5},
    }

    try:
        context['categories'] = get_categories()

        if request.method == 'POST':
            try:
                category = request.POST.get('category', '')
                year = int(request.POST.get('year'))
                month = int(request.POST.get('month'))
                copies = max(0, int(request.POST.get('copies')))
                context['form'] = {'category': category, 'year': year, 'month': month, 'copies': copies}

                if category not in context['categories'] or not 1 <= month <= 12:
                    raise ValueError('Please choose a valid category and month.')

                result = predict_demand(category, year, month)
                needed = math.ceil(result['demand'] / LOANS_PER_COPY_PER_MONTH)
                result.update(copies=copies, needed=needed, extra=max(0, needed - copies))
                context['result'] = result
            except (TypeError, ValueError) as exc:
                msg = str(exc)
                context['error'] = msg if 'invalid literal' not in msg and 'NoneType' not in msg \
                    else 'Please fill all the fields with valid numbers.'
    except ModelNotReady as exc:
        context['error'] = str(exc)

    return render(request, 'predict.html', context)
