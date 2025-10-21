from django.contrib import admin
from .models import User,LoginHistory, Badge, UserBadge,Friendship, Device
# Register your models here.
class UserDisplay(admin.ModelAdmin):
    list_display = ('email','id')
    search_fields  = ('email','id')

admin.site.register(User,UserDisplay)
admin.site.register(LoginHistory)
admin.site.register(Badge)
admin.site.register(UserBadge)
admin.site.register(Friendship)
admin.site.register(Device)

