from django.shortcuts import render, redirect,get_object_or_404,redirect
from django.contrib.auth.decorators import login_required
from .models import Expense, CATEGORY_CHOICES, Budget
from .forms import ExpenseForm,RegisterForm, BudgetForm
from django.contrib import messages
from django.contrib.auth import login
from django.db import models
from django.db.models import Sum
from django.contrib.auth import authenticate, login, logout
from datetime import datetime
from django.db.models.functions import TruncDay, TruncMonth
import openpyxl
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from django.http import HttpResponse
from django.utils import timezone
import calendar

@login_required
def dashboard(request):
    expenses = Expense.objects.filter(user=request.user).order_by('-date')
    total = expenses.aggregate(Sum('amount'))['amount__sum'] or 0

    # Filtering
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    category = request.GET.get('category')

    if start_date:
        expenses = expenses.filter(date__gte=start_date)
    if end_date:
        expenses = expenses.filter(date__lte=end_date)
    if category and category != 'All':
        expenses = expenses.filter(category=category)

    filtered_total = expenses.aggregate(Sum('amount'))['amount__sum'] or 0

    context = {
        'expenses': expenses,
        'total': filtered_total,
        'categories': [c[0] for c in CATEGORY_CHOICES], # use imported CATEGORY_CHOICES
        'selected_category': category or 'All',
        'start_date': start_date or '',
        'end_date': end_date or '',
    }
    return render(request, 'expenses/dashboard.html', context)

@login_required
def add_expense(request):
    form = ExpenseForm(request.POST or None)
    if form.is_valid():
        expense = form.save(commit=False)
        expense.user = request.user
        expense.save()
        return redirect('dashboard')
    return render(request, 'expenses/add_expense.html', {'form': form, 'edit': False})

@login_required
def edit_expense(request, expense_id):
    expense = get_object_or_404(Expense, id=expense_id, user=request.user)
    if request.method == 'POST':
        form = ExpenseForm(request.POST, instance=expense)
        if form.is_valid():
            form.save()
            return redirect('dashboard')
    else:
        form = ExpenseForm(instance=expense)
    return render(request, 'expenses/add_expense.html', {'form': form, 'edit': True})

@login_required
def delete_expense(request, id):
    expense = get_object_or_404(Expense, id=id, user=request.user)
    expense.delete()
    return redirect('dashboard')

def register(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():  # Validates password match and all fields
            user = form.save()
            login(request, user)  # Automatically log in
            messages.success(request, "Account created successfully!")
            return redirect('dashboard')  # Redirect to dashboard
        else:
            # Form is invalid → show errors
            messages.error(request, "Please correct the errors below.")
    else:
        form = RegisterForm()
    return render(request, 'registration/register.html', {'form': form})


# Custom Login
def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            messages.success(request, "Logged in successfully!")
            return redirect('dashboard')
        else:
            messages.error(request, "Invalid username or password")
    return render(request, 'registration/login.html')

# Custom Logout
def logout_view(request):
    logout(request)
    messages.success(request, "Logged out successfully!")
    return redirect('login')

@login_required
def budget_list(request):
    today = timezone.now()
    current_month = today.strftime('%b')  # 'Jan', 'Feb', etc.
    current_year = today.year

    # Filter values from GET
    month = request.GET.get('month', current_month)
    year = int(request.GET.get('year', current_year))

    # Filter budgets for this month/year
    budgets = Budget.objects.filter(month=month, year=year)

    # Build budget_data with spent/remaining/percent/over
    budget_data = []
    month_number = list(calendar.month_abbr).index(month)  # convert 'Jan'->1
    for b in budgets:
        spent = Expense.objects.filter(
            category=b.category,
            date__year=year,
            date__month=month_number
        ).aggregate(total=models.Sum('amount'))['total'] or 0

        remaining = float(b.amount) - spent
        percent = (spent / float(b.amount) * 100) if b.amount else 0
        over = spent > float(b.amount)

        budget_data.append({
            'budget': b,
            'spent': spent,
            'remaining': remaining,
            'percent': percent,
            'over': over
        })

    # Generate month/year filter dynamically from actual Budget data
    months = [m[0] for m in Budget._meta.get_field('month').choices]

    # Years available in database + current year if not present
    years_in_db = Budget.objects.values_list('year', flat=True).distinct()
    years = sorted(list(set(list(years_in_db) + [current_year])))

    context = {
        'budget_data': budget_data,
        'month': month,
        'year': year,
        'months': months,
        'years': years,
    }

    return render(request, 'expenses/budget_list.html', context)

@login_required
def add_budget(request):
    current_month = timezone.now().strftime('%b')
    current_year = timezone.now().year

    if request.method == 'POST':
        category = request.POST['category']
        amount = request.POST['amount']
        month = request.POST['month']
        year = request.POST['year']

        Budget.objects.create(
            category=category,
            amount=amount,
            month=month,
            year=year
        )
        return redirect('budget_list')  # Redirect to your budget list page

    # Get MONTH_CHOICES and CATEGORY_CHOICES from the model
    months = [m[0] for m in Budget._meta.get_field('month').choices]
    categories = [c[0] for c in Budget._meta.get_field('category').choices]

    context = {
        'months': months,
        'selected_month': current_month,
        'selected_year': current_year,
        'CATEGORY_CHOICES': categories,  # pass categories to template
    }

    return render(request, 'expenses/add_budget.html', context)



@login_required
def analytics_dashboard(request):
    from datetime import datetime
    now = datetime.now()
    month = now.month
    year = now.year

    expenses = Expense.objects.filter(
        user=request.user,
        date__month=month,
        date__year=year
    )

    # Category wise
    category_data = expenses.values('category').annotate(total=Sum('amount'))

    # Day wise
    daily_data = expenses.annotate(day=TruncDay('date')).values('day').annotate(total=Sum('amount')).order_by('day')

    # Month wise (for last 6 months)
    monthly_data = (
        Expense.objects.filter(user=request.user)
        .annotate(month=TruncMonth('date'))
        .values('month')
        .annotate(total=Sum('amount'))
        .order_by('month')[:6]
    )

    context = {
        'category_labels': [c['category'] for c in category_data],
        'category_totals': [float(c['total']) for c in category_data],

        'daily_labels': [d['day'].strftime("%d %b") for d in daily_data],
        'daily_totals': [float(d['total']) for d in daily_data],

        'monthly_labels': [m['month'].strftime("%b %Y") for m in monthly_data],
        'monthly_totals': [float(m['total']) for m in monthly_data],
    }

    return render(request, 'expenses/analytics.html', context)


@login_required
def export_excel(request):
    expenses = Expense.objects.filter(user=request.user)

    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Expenses"

    ws.append(["Title", "Amount", "Category", "Date", "Note"])

    for e in expenses:
        ws.append([e.title, e.amount, e.category, e.date.strftime("%Y-%m-%d"), e.note or ""])

    response = HttpResponse(
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
    response['Content-Disposition'] = 'attachment; filename=expenses.xlsx'

    wb.save(response)
    return response


@login_required
def export_pdf(request):
    expenses = Expense.objects.filter(user=request.user)

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="expenses.pdf"'

    p = canvas.Canvas(response, pagesize=A4)
    width, height = A4

    y = height - 50
    p.setFont("Helvetica", 10)

    p.drawString(50, y, "Expense Report")
    y -= 30

    for e in expenses:
        line = f"{e.date} | {e.title} | {e.category} | ₹{e.amount}"
        p.drawString(50, y, line)
        y -= 20

        if y < 50:
            p.showPage()
            p.setFont("Helvetica", 10)
            y = height - 50

    p.save()
    return response
