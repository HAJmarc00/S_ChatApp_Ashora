from django.contrib import admin
from .models import Notification

@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('id', 'recipient', 'actor', 'verb', 'target', 'timestamp', 'is_read')
    list_filter = ('is_read', 'timestamp', 'actor')
    search_fields = ('recipient__username', 'actor__username', 'verb', 'target')
    readonly_fields = ('timestamp',)
    ordering = ('-timestamp',)
    autocomplete_fields = ('recipient', 'actor')  # اگه تعداد کاربران زیاد باشه، این کمک می‌کنه

    # اگر بخوای فقط به ادمین اجازه ویرایش وضعیت خواندن نوتیفیکیشن رو بدی:
    def get_readonly_fields(self, request, obj=None):
        if obj:
            # فقط فیلد is_read قابل ویرایش باشد
            return ('recipient', 'actor', 'verb', 'target', 'timestamp')
        return super().get_readonly_fields(request, obj)

