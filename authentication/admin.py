from django.contrib import admin
from .models import User
# Register your models here.
class UserDisplay(admin.ModelAdmin):
    list_display = ('email','id')
    search_fields  = ('email','id')

admin.site.register(User,UserDisplay)