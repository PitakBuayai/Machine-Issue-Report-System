from django.urls import path, include
from .views import (
    MachineListApiView,
    IssueListApiView,
    AllIssueListApiView,
    IssueListView,
    IssueReportsPerMachine,
    ResolveIssue,
    TopCommonWords
)

urlpatterns = [
    path('add-machines', MachineListApiView.as_view()),
    path('add-issues', IssueListApiView.as_view()),
    path('all-issues', AllIssueListApiView.as_view()),
    path('filter-issues', IssueListView.as_view()),
    path('issues-per-machine', IssueReportsPerMachine.as_view()),
    path('top-common-words', TopCommonWords.as_view()),
    path('resolve-issues/<int:issue_id>/', ResolveIssue.as_view())
]