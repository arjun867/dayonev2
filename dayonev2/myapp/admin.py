from django.contrib import admin

# Register your models here.
from .models import CustomUser,Task,Pomodoro,Product

admin.site.register(CustomUser)
admin.site.register(Task)
admin.site.register(Pomodoro)
admin.site.register(Product)