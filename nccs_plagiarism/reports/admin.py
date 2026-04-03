from django.contrib import admin
from .models import Report

@admin.register(Report)
class ReportAdmin(admin.ModelAdmin):
    list_display = ('title', 'report_type', 'uploaded_at', 'file')
    list_filter = ('report_type',)
    ordering = ('-uploaded_at',)