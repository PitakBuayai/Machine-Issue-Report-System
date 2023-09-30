from django.contrib import admin

# Register your models here.

from MachineIssueReportSystem.models import *


class MachineAdmin(admin.ModelAdmin):
    fields = ['name']

admin.site.register(Machine, MachineAdmin)

class IssueAdmin(admin.ModelAdmin):
    fields = ['machine', 'title','description', 'timestamp','status']

admin.site.register(Issue, IssueAdmin)

class IssueStatusHistoryAdmin(admin.ModelAdmin):
    fields = ['issue', 'status','timestamp', 'comment']

admin.site.register(IssueStatusHistory, IssueStatusHistoryAdmin)
