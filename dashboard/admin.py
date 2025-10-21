from django.contrib import admin
from .models import Notifications, PrivacyPolicy, TremsAndCondition
# Register your models here.
admin.site.register(Notifications)
admin.site.register(PrivacyPolicy)
admin.site.register(TremsAndCondition)