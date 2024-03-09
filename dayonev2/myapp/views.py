
from django.shortcuts import render, redirect,get_object_or_404,reverse,HttpResponse
# from .forms import CustomUserCreationForm, CustomAuthenticationForm
from django.contrib.auth import login, authenticate,logout
from .models import Task,Pomodoro,CustomUser,Product

from django.contrib.auth.decorators import login_required
from datetime import datetime,timedelta
from django.db.models.functions import TruncDay, TruncWeek, TruncMonth,TruncYear

from django.utils import timezone

from django.http import JsonResponse
import json
from django.db.models.functions import ExtractWeek,ExtractMonth,ExtractYear
from django.db.models import Count

from django.shortcuts import get_object_or_404
# from django.db.models.functions import TruncYear
from django.db import IntegrityError
from django.utils.crypto import get_random_string


# def register_view(request):
#     if request.method == 'POST':
#         username = request.POST['username']
#         email = request.POST['email']
#         password = request.POST['password']
#         nationality = request.POST['nationality']
#         social_media_url = request.POST.get('social_media_url', email)

#         while True:
#             try:
#                 user = CustomUser.objects.create_user(username=username, email=email, password=password, nationality=nationality)
#                 break
#             except IntegrityError:
#                 # Append a random string to the username to make it unique
#                 new_username = f"{username}_{get_random_string(length=5)}"
#                 continue

#         login(request, user)
#         return redirect('home')

#     return render(request, 'register.html')

from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

@login_required
def ranking_view(request):

    print(request.GET)  # Print request parameters

    gender_filter = request.GET.get('gender', '')
    goal_filter = request.GET.get('goal', '')
    # rank_min = request.GET.get('rank_min', None)
    # rank_max = request.GET.get('rank_max', None)

    users = CustomUser.objects.order_by('-total_pomodoros')

    # if rank_min and rank_max:
    #     rank_min = int(rank_min)  # Convert string to integer
    #     rank_max = int(rank_max)  # Convert string to integer
    #     users = users.filter(rank__gte=rank_min, rank__lte=rank_max)

    for user in users:
        user.net_worth = user.total_pomodoros * 25
    
    if gender_filter:
        users = users.filter(gender=gender_filter)

    if goal_filter:
        users = users.filter(future_goal=goal_filter)

    paginator = Paginator(users, 50)  # Show 50 users per page

    page_number = request.GET.get('page')
    try:
        users_page = paginator.page(page_number)
    except PageNotAnInteger:
        users_page = paginator.page(1)
    except EmptyPage:
        users_page = paginator.page(paginator.num_pages)

    current_user_rank = users.filter(total_pomodoros__gt=request.user.total_pomodoros).count() + 1

    context = {
        'users': users_page,
        'current_user_rank': current_user_rank,
        'current_user': request.user,
    }

    print(users)

    return render(request, 'ranking.html', context)

def register_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password']
        nationality = request.POST['nationality']
        social_media_url = request.POST.get('social_media_url', email)
        gender = request.POST['gender']
        age = request.POST['age']
        college_or_workplace = request.POST['college_or_workplace']
        future_goal = request.POST['future_goal']
        other_goal_text = request.POST.get('other_goal_text', '')

        while True:
            try:
                user = CustomUser.objects.create_user(
                    username=username,
                    email=email,
                    password=password,
                    nationality=nationality,
                    social_media_url=social_media_url,
                    gender=gender,
                    age=age,
                    college_or_workplace=college_or_workplace,
                    future_goal=future_goal,
                    other_goal_text=other_goal_text
                )
                break
            except IntegrityError:
                # Append a random string to the username to make it unique
                new_username = f"{username}_{get_random_string(length=5)}"
                continue

        login(request, user)
        return redirect('home')

    return render(request, 'register.html')


def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']

        user = authenticate(username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('home')
        else:
            # Handle invalid login credentials
            return render(request, 'login.html', {'error': 'Invalid username or password'})

    return render(request, 'login.html')


def logout_view(request):
    logout(request)
    return redirect('home')  

def about(request):
    return render(request,"about.html")

def help(request):
    return render(request,"help.html")


@login_required
def get_current_user_id(request):
    user_id = request.user.id
    return JsonResponse({'user_id': user_id})

@login_required
def convert_pomodoros_to_currency(request):
    if request.method == 'POST':
        user = request.user
        # No need to calculate virtual_currency, use the virtual_currency_balance property
        virtual_currency = user.virtual_currency_balance
        print("balance in views",virtual_currency)
        # No need to update user.virtual_currency, as it's calculated dynamically
        return JsonResponse({'success': True, 'virtual_currency': virtual_currency})
    return JsonResponse({'success': False, 'error': 'Invalid request method'})

# @login_required
# def convert_pomodoros_to_currency(request):
#     if request.method == 'POST':
#         user = request.user
#         virtual_currency = getattr(user, 'virtual_currency_balance', 0)
#         print("balance in views", virtual_currency)
#         return JsonResponse({'success': True, 'virtual_currency': virtual_currency})
#     return JsonResponse({'success': False, 'error': 'Invalid request method'})

# @login_required
# def convert_pomodoros_to_currency(request):
#     if request.method == 'POST':
#         user = request.user
#         # Calculate total earned virtual currency from completed Pomodoros
#         total_earned = user.total_pomodoros * 25

#         # Calculate total spent on products purchased before reaching current balance
#         purchased_products = Product.objects.filter(
#             purchased_by=user,
#             # cost_in_pomodoros__lt=total_earned // 25  # Filter based on total earned virtual currency spent
#         )
#         total_spent = sum(product.cost_in_pomodoros for product in purchased_products)

#         # Calculate virtual currency balance after deducting total spent
#         virtual_currency_balance = total_earned - (total_spent if total_spent else 0)

#         return JsonResponse({'success': True, 'virtual_currency': virtual_currency_balance})
#     return JsonResponse({'success': False, 'error': 'Invalid request method'})


@login_required
def purchase_product(request, product_id):
    if request.method == 'POST':
        user = request.user
        product = Product.objects.get(pk=product_id)
        if user.virtual_currency_balance >= product.cost_in_pomodoros*25:
            if not product.purchased_by.filter(id=user.id).exists():  # Check if user has already purchased the product
                user.virtual_currency_balance -= product.cost_in_pomodoros*25
                user.save()
                product.purchased_by.add(user)  # Add the user to the list of purchasers
                product.save()
                print("product cost in views",product.cost_in_pomodoros)
                print("virtual balance in views",user.virtual_currency_balance)
                return JsonResponse({'success': True, 'virtual_currency_balance': user.virtual_currency_balance})
            else:
                return JsonResponse({'success': False, 'error': 'Product already purchased'})
        else:
            return JsonResponse({'success': False, 'error': 'Insufficient virtual currency'})
    return JsonResponse({'success': False, 'error': 'Invalid request method'})


def home(request):
    if request.user.is_authenticated:
        # Retrieve all products from the database
        products = Product.objects.all()

        # Create a dictionary to store products grouped by category
        category_products = {}
        for category, _ in Product.CATEGORY_CHOICES:
            category_products[category] = products.filter(category=category)

        # Retrieve tasks and completed tasks
        tasks = Task.objects.filter(user=request.user, completed=False).order_by('-scheduled_datetime')
        completed_tasks = Task.objects.filter(user=request.user, completed=True).order_by('-created_time')[:15]

        # Render the template with the retrieved data
        return render(request, "home.html", {
            'tasks': tasks,
            'completed_tasks': completed_tasks,
            'category_products': category_products
        })
    else:
        return render(request, "home.html", {'tasks': [], 'completed_tasks': [],})
    
@login_required
def post(request):
        taskId = request.POST.get('taskId')
        userId = request.POST.get('userId')
        
        try:
            task = Task.objects.get(id=taskId)
            user = CustomUser.objects.get(id=userId)
            pomodoro = Pomodoro.objects.create(task=task, user=user)
            return JsonResponse({'id': pomodoro.id})
        except (Task.DoesNotExist, CustomUser.DoesNotExist) as e:
            return JsonResponse({'error': str(e)}, status=400)

@login_required
def get_daily_pomodoro_count(request):
    # Get today's date
    today = timezone.now().date()
    # Get the count of Pomodoros for today for the current user
    daily_count = request.user.pomodoros.filter(created_at__date=today).count()
    return JsonResponse({'daily_count': daily_count})

@login_required
def get_weekly_pomodoro_count(request):
    # Get the start date of the current week (assuming Sunday is the first day of the week)
    today = timezone.now().date()
    start_of_week = today - timezone.timedelta(days=today.weekday())

    # Generate a list of dates for the entire week
    week_dates = [start_of_week + timezone.timedelta(days=i) for i in range(7)]

    # Query your database to get the daily counts for the current week for the current user
    daily_counts = [
        {'day': date.strftime('%Y-%m-%d'), 'count': request.user.pomodoros.filter(created_at__date=date).count()} 
        for date in week_dates
    ]

    return JsonResponse({'weekly_counts': daily_counts})

@login_required
def get_monthly_pomodoro_count(request):
    # Get the current year and month
    current_year = timezone.now().year
    current_month = timezone.now().month

    # Query your database to get the monthly counts for the current year and month for the current user
    monthly_counts = [
        {'month': month, 'count': request.user.pomodoros.filter(created_at__year=current_year, created_at__month=month).count()} 
        for month in range(1, 13)
    ]

    return JsonResponse({'monthly_counts': monthly_counts})


@login_required
def get_yearly_pomodoro_count(request):
    # Get the current year
    current_year = timezone.now().year

    # Get the year-wise breakdown of Pomodoro counts for each year for the current user
    yearly_counts = (
        request.user.pomodoros
        .filter(created_at__year=current_year)
        .values('created_at__year')
        .annotate(count=Count('id'))
        .order_by('created_at__year')
    )

    # Convert the annotated queryset to a list of dictionaries
    yearly_counts_list = [{'year': item['created_at__year'], 'count': item['count']} for item in yearly_counts]

    return JsonResponse({'yearly_counts': yearly_counts_list})

@login_required
def get_total_pomodoro_count(request):
    # Get the total count of Pomodoros for the current user
    total_count = request.user.pomodoros.count()
    return JsonResponse({'total_count': total_count})

@login_required
def task_list(request):
    tasks = Task.objects.filter(user=request.user, completed=False).order_by('-scheduled_datetime')
    completed_tasks = Task.objects.filter(user=request.user, completed=True).order_by('-scheduled_datetime')
    return render(request, 'home.html', {'tasks': tasks, 'completed_tasks': completed_tasks})

@login_required
def create_task(request):
    if request.method == 'POST':
        title = request.POST.get('title')
        priority = request.POST.get('priority', 'green')
        scheduled_datetime_str = request.POST.get('scheduled_datetime')

        # Set a default value if scheduled_datetime_str is not provided
        if scheduled_datetime_str:
            scheduled_datetime = datetime.strptime(scheduled_datetime_str, '%Y-%m-%dT%H:%M')
        else:
            scheduled_datetime = None  # Set a default value (e.g., None) when no datetime is provided

        # Create the task
        task = Task.objects.create(
            user=request.user,
            title=title,
            priority=priority,
            scheduled_datetime=scheduled_datetime,
        )

        # Fetch tasks and completed_tasks
        tasks = Task.objects.filter(user=request.user, completed=False).order_by('-scheduled_datetime')
        completed_tasks = Task.objects.filter(user=request.user, completed=True).order_by('-created_time')[:15]

        # Retrieve all products from the database
        products = Product.objects.all()

        # Create a dictionary to store products grouped by category
        category_products = {}
        for category, _ in Product.CATEGORY_CHOICES:
            category_products[category] = products.filter(category=category)

        # Pass the tasks and completed_tasks to the template context
        return render(request, 'home.html', {'tasks': tasks, 'completed_tasks': completed_tasks, 'category_products': category_products})
    else:
        # Handle GET request or other methods
        return render(request, 'home.html')

@login_required
def complete_task(request, task_id):
    task = get_object_or_404(Task, id=task_id, user=request.user)
    task.completed = True
    task.save()
    return redirect('home')

@login_required
def remark(request, task_id):
    task = Task.objects.get(id=task_id)
    task.completed = False
    task.save()
    return redirect('home')


