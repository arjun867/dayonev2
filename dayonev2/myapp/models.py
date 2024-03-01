from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver
from django.utils import timezone
from django.contrib.auth import get_user_model

from django.db.models import Sum


class CustomUser(AbstractUser):
    NATIONALITY_CHOICES = [
        ('indian', 'Indian'),
        ('non-indian', 'Non-Indian'),
    ]

    SOCIAL_MEDIA_CHOICES = [
            ('facebook', 'Facebook'),
            ('twitter', 'Twitter'),
            ('instagram', 'Instagram'),
            ('linkedin', 'LinkedIn'),
            ('email', 'Email'),
        ]

    social_media_url = models.URLField(blank=True, null=True)

    nationality = models.CharField(max_length=20, choices=NATIONALITY_CHOICES)
    total_pomodoros = models.IntegerField(default=0)
    virtual_currency_balance = models.IntegerField(default=0)

    def purchase_product(self, product):
        if self.virtual_currency_balance >= product.cost_in_pomodoros:
            self.virtual_currency_balance -= product.cost_in_pomodoros
            self.save()
            return True
        return False
    @property
    def virtual_currency_balance(self):
        return self.total_pomodoros * 25
    @virtual_currency_balance.setter
    def virtual_currency_balance(self, value):
        self.total_pomodoros = value // 25

    def __str__(self):
        return self.username

class Task(models.Model):
    PRIORITY_CHOICES = [
        ('red', 'Red'),
        ('green', 'Green'),
        ('yellow', 'Yellow'),
    ]
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, default=None, blank=True, null=True)
    title = models.CharField(max_length=150)
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default='green')
    created_time = models.DateTimeField(auto_now_add=True)
    completed = models.BooleanField(default=False)
    scheduled_datetime = models.DateTimeField(default=timezone.now, blank=True, null=True)

    @property
    def priority_icon(self):
        if self.priority == 'red':
            return '❤️'
        elif self.priority == 'yellow':
            return '💛'
        else:
            return '💚'

    def __str__(self):
        return self.title

class Pomodoro(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='pomodoros')
    task = models.ForeignKey(Task, on_delete=models.CASCADE)
    start_time = models.DateTimeField(default=timezone.now)
    end_time = models.DateTimeField(null=True, blank=True)
    skipped = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    virtual_currency_earned = models.IntegerField(default=0)

    def __str__(self):
        return f"Pomodoro for {self.user.username} at {self.start_time}"

User = get_user_model()
class Product(models.Model):
    CATEGORY_CHOICES = [
        ('clothes','Clothes'),
        ('watches', 'High-end Watches'),
        ('Cars', 'Luxury Cars'),
        ('jewelry', 'Fine Jewelry'),
        ('real_estate', 'Luxury Real Estate'),
        ('private_jets', 'Private Jets'),
        ('yachts', 'Yachts'),
        ('art_and_collectibles', 'Art and Collectibles'),
        ('exotic_vacations', 'Exotic Vacations'),
    ]
    name = models.CharField(max_length=100)
    description = models.TextField()
    cost_in_pomodoros = models.IntegerField()
    # image = models.ImageField(upload_to='product_images/')
    category = models.CharField(max_length=100, choices=CATEGORY_CHOICES,default='Uncategorized')

    purchased_by = models.ManyToManyField(User, related_name='purchased_products', blank=True)

    cost_in_virtual_currency = models.IntegerField(default=0)  # Assuming virtual currency is represented as an integer

    @property
    def purchased_by_user(self):
        return self.purchased_by.filter(id=self.id).exists()
    
    def __str__(self):
        return self.name


# @receiver(post_save, sender=Pomodoro)
# def update_user_pomodoro_count(sender, instance, created, **kwargs):
#     if created:
#         user = instance.user
#         user.total_pomodoros = Pomodoro.objects.filter(user=user).count()
#         total_cost = Product.objects.filter(purchased_by=user).aggregate(total_cost=Sum('cost_in_pomodoros'))['total_cost']
#         user.virtual_currency_balance = user.total_pomodoros * 25 - (total_cost if total_cost else 0)


@receiver(post_save, sender=Pomodoro)
def update_user_pomodoro_count(sender, instance, created, **kwargs):
    if created:
        user = instance.user
        user.total_pomodoros = Pomodoro.objects.filter(user=user).count()

        # Calculate total earned virtual currency from completed Pomodoros
        total_earned = user.total_pomodoros * 25

        # Calculate total spent on products purchased before reaching current balance
        purchased_products = Product.objects.filter(
            purchased_by=user,
        )
        total_spent = 25*sum(product.cost_in_virtual_currency for product in purchased_products)
        print("total earned in models file", total_earned)
        print("total spent in models file", total_spent)
        
        user.virtual_currency_balance = total_earned - total_spent
        user.save()



@receiver(post_delete, sender=Pomodoro)
def decrease_user_pomodoro_count(sender, instance, **kwargs):
    user = instance.user
    user.total_pomodoros = Pomodoro.objects.filter(user=user).count()
    user.virtual_currency_balance = user.total_pomodoros * 25
    user.save()
