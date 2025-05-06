from django.contrib import admin

# Register your models here.
from .models import DetectionHistory
from django.utils.timezone import now
import pytz

ist = pytz.timezone('Asia/Kolkata')
now_ist = now().astimezone(ist)

@admin.register(DetectionHistory)
class DetectionHistoryAdmin(admin.ModelAdmin):
    list_display = ('user', 'detection_type', 'input_file', 'output_file', 'created_at')
    ordering = ['-created_at']