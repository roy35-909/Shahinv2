from django.contrib import admin

# Register your models here.
from .models import Quote
from .models import UserQuote
from .models import UserSchedule


admin.site.register(Quote)
admin.site.register(UserQuote)
admin.site.register(UserSchedule)