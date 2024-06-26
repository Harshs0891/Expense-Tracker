from django.shortcuts import render,redirect
from .forms import ExpenseForm
from .models import Expense
from django.db.models import Sum
import datetime
from django.contrib import messages
from django.contrib.auth.decorators import login_required
# Create your views here.

#---------------authentication--------------
from .forms import LoginForm,RegisterForm
from django.contrib.auth import login,authenticate,logout

# ----------------------------------------User Login and Registration----------------------------------------
def sign_up(request):
    if request.method == 'GET':
        form=RegisterForm()
        return render(request,'myapp/register.html',{'form':form})
    
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request,user)
            messages.success(request,'User created and signed up successfully')
            return redirect('index')
        else:
            messages.error(request,"Enter Valid Information")
            return redirect('register')
            # return render(request,'myapp/register.html',{'form':form})

    
    return render(request,'myapp/register.html',{'form':form})



def user_login(request):
    form = LoginForm()
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            user = authenticate(username = form.cleaned_data['username'],password = form.cleaned_data['password'])

            if user is not None:
                login(request,user)
                messages.success(request,'Logged In Successfully!')
                return redirect('index')
            else:
                messages.error(request,"Enter valid credentials!!")
                return redirect('login')
            
            
    
    return render(request,'myapp/login.html',{'form':form})

def logout_user(request):
    logout(request)
    messages.success(request,'Logged Out Successfully!')
    return redirect('login')














#----------------------------------------------------- Code for Expense tracker -----------------------------------------------------


def about(request):
    return render(request,'myapp/about.html')

@login_required(login_url='user/login/')
def index(request):
    if request.method=='POST':
        form = ExpenseForm(request.POST)
        if form.is_valid():
            expense = form.save(commit=False)
            expense.user = request.user
            messages.success(request,"Expense added Successfully !!!")
            expense.save() 
            return redirect('index')
        else:
            messages.error(request,"Failed to add Expense")
            return redirect('index')

        

    
    expenses = Expense.objects.filter(user=request.user)

    total_expenses = expenses.aggregate(Sum('amount'))

    #logic to calculate 365 days expenses
    last_year = datetime.date.today() - datetime.timedelta(days=365)
    data = Expense.objects.filter(date__gt=last_year,user=request.user)
    yearly_sum = data.aggregate(Sum('amount'))
    # print(yearly_sum)
    
    
    #logic to calculate 30 days expenses
    last_month = datetime.date.today() - datetime.timedelta(days=30)
    data = Expense.objects.filter(date__gt=last_month,user=request.user)
    monthly_sum = data.aggregate(Sum('amount'))
    # print(monthly_sum)
    
    
    #logic to calculate 7 days expenses
    last_week = datetime.date.today() - datetime.timedelta(days=7)
    data = Expense.objects.filter(date__gt=last_week,user=request.user)
    weekly_sum = data.aggregate(Sum('amount'))
    # print(weekly_sum)



    daily_sums = Expense.objects.filter(user=request.user).values('date').order_by('date').annotate(sum=Sum('amount'))
    # print(daily_sum)


    categorical_sums = Expense.objects.filter(user=request.user).values('category').order_by('category').annotate(sum=Sum('amount'))
    # print(categorical_sums)



    expense_form = ExpenseForm()
    return render(request,'myapp/index.html',{'expense_form':expense_form,'expenses':expenses,'total_expenses':total_expenses,'yearly_sum':yearly_sum,'weekly_sum':weekly_sum,'monthly_sum':monthly_sum,'daily_sums':daily_sums,'categorical_sums':categorical_sums})

@login_required(login_url='user/login/')
def edit(request,id):
    expense = Expense.objects.get(id=id)
    expense_form = ExpenseForm(instance=expense)

    if request.method == 'POST':
        expense = Expense.objects.get(id=id)
        form = ExpenseForm(request.POST,instance=expense)
        if form.is_valid():
            form.save()
            messages.success(request,'Expense edited Successfully')
            return redirect('index')
    return render(request,'myapp/edit.html',{'expense_form':expense_form})


@login_required(login_url='user/login/')
def delete(request,id):
    if request.method == 'POST' and 'delete' in request.POST:
        expense = Expense.objects.get(id=id)
        expense.delete()
        messages.error(request,'Expense deleted Successfully')
    return redirect('index')
