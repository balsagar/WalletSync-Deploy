from django.shortcuts import render, redirect
from django.utils import timezone
from collections import defaultdict
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from .models import Expense, Budget
from .forms import UserRegistrationForm, ExpenseForm, BudgetForm
from django.contrib import messages
from django.db.models import Sum
from .models import Expense

# Home Page
def home(request):
    return render(request, 'home.html')

# User Registration
def register(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Registration successful!')
            return redirect('login')
    else:
        form = UserRegistrationForm()
    return render(request, 'register.html', {'form': form})

# User Login
def user_login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            return redirect('home')
        else:
            messages.error(request, 'Invalid credentials')
    return render(request, 'login.html')

# User Logout
def user_logout(request):
    logout(request)
    return redirect('login')

# Budget View
@login_required
def budget(request):
    if request.method == 'POST':
        form = BudgetForm(request.POST)
        if form.is_valid():
            budget = form.save(commit=False)
            budget.user = request.user
            budget.save()
            messages.success(request, 'Budget set successfully!')
    else:
        form = BudgetForm()
    budget = Budget.objects.filter(user=request.user).last()
    return render(request, 'budget.html', {'form': form, 'budget': budget})

# Expense Entry
@login_required
def expenses(request):
    if request.method == 'POST':
        form = ExpenseForm(request.POST)
        if form.is_valid():
            expense = form.save(commit=False)
            expense.user = request.user
            expense.save()
            messages.success(request, 'Expense added successfully!')
    else:
        form = ExpenseForm()
    expenses = Expense.objects.filter(user=request.user).order_by('-date')
    return render(request, 'expenses.html', {'form': form, 'expenses': expenses})

# Weekly Summary
@login_required
def summary(request):
    # Assuming you already have budget and total_spent variables
    budget = 1000  # Replace with your actual budget logic
    total_spent = 400  # Replace with your actual spent logic

    # Calculate percentage
    if budget > 0:
        percentage_spent = (total_spent / budget) * 100
    else:
        percentage_spent = 0

    context = {
        'budget': budget,
        'total_spent': total_spent,
        'percentage_spent': round(percentage_spent),  # round to make it cleaner
    }

    return render(request, 'summary.html', context)


# Expense Analysis
@login_required
def analysis(request):
    # Retrieve all expenses for the current user
    expenses = Expense.objects.filter(user=request.user)

    # Categorize expenses by category (you can change this to day of the week or other field if needed)
    expenses_by_category = defaultdict(int)
    for expense in expenses:
        expenses_by_category[expense.category] += expense.amount  # Sum amounts by category

    categories = list(expenses_by_category.keys())  # Categories for the x-axis
    amounts = list(expenses_by_category.values())  # Corresponding expense amounts for the y-axis

    # Pass data to template
    data = {
        'categories': categories,
        'amounts': amounts
    }

    return render(request, 'analysis.html', data)