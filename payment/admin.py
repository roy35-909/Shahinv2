from django.contrib import admin
from .models import Payment, SubscriptionPlan
# Register your models here.
admin.site.register(Payment)
admin.site.register(SubscriptionPlan)