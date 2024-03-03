from django.urls import path
from django.contrib.auth import views as auth_views
from . import views
from django.urls import path


from django.contrib.auth.views import (
    # LoginView,
    LogoutView, 
    PasswordResetView, 
    PasswordResetDoneView, 
    PasswordResetConfirmView,
    PasswordResetCompleteView
)


urlpatterns = [

    path('accounts/login/', auth_views.LoginView.as_view(next_page='home'), name='login'),
    path('accounts/logout/', views.logout_view, name='logout'),
    # path('logout/',views.logout_view,name="logout"),
    # path('accounts/logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('register/', views.register_view, name='register'),
    

    # path('register/', views.register_view, name='register'),
    # path('login/', views.login_view, name='login'),
    # path('logout/', views.logout_view, name='logout'),
    path('password-reset/', 
     PasswordResetView.as_view(
        template_name='registration/password_reset.html',
        html_email_template_name='registration/password_reset_email.html'
    ),
    name='password-reset'
    ),
    path('password-reset/done/', PasswordResetDoneView.as_view(template_name='registration/reset_password_done.html'),name='password_reset_done'),
    path('password-reset-confirm/<uidb64>/<token>/', PasswordResetConfirmView.as_view(template_name='registration/password_reset_confirm.html'),name='password_reset_confirm'),
    path('password-reset-complete/',PasswordResetCompleteView.as_view(template_name='registration/password_reset_complete.html'),name='password_reset_complete'),
    
    path('ranking/', views.ranking_view, name='ranking'),
    path('', views.home, name='home'),
    path('about/',views.about,name="about"),
    path('help/',views.help,name="help"),
    path('tasks/', views.task_list, name='task-list'),
    path('addtask/',views.create_task,name='add_task'),
    path('tasks/<int:task_id>/complete/', views.complete_task, name='complete-task'),
    path('remark/<int:task_id>/', views.remark, name='remark'),

    path('add_pomodoro/', views.post, name='add_pomodoro'),
    path('get_current_user_id/', views.get_current_user_id, name='get_current_user_id'),
    
    path('get_daily_pomodoro_count/', views.get_daily_pomodoro_count, name='get_daily_pomodoro_count'),
    path('get_weekly_pomodoro_count/', views.get_weekly_pomodoro_count, name='get_weekly_pomodoro_count'),
    path('get_monthly_pomodoro_count/', views.get_monthly_pomodoro_count, name='get_monthly_pomodoro_count'),
    path('get_yearly_pomodoro_count/', views.get_yearly_pomodoro_count, name='get_yearly_pomodoro_count'),
    path('get_total_pomodoro_count/', views.get_total_pomodoro_count, name='get_total_pomodoro_count'),

    path('convert_pomodoros_to_currency/', views.convert_pomodoros_to_currency, name='convert_pomodoros_to_currency'),
    path('purchase_product/<int:product_id>/', views.purchase_product, name='purchase_product'),

]
