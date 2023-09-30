
from rest_framework.views import APIView
from rest_framework import generics
from rest_framework.response import Response
from rest_framework import status
from .models import Machine, Issue, IssueStatusHistory
from .serializers import MachineSerializer, IssueSerializer, IssueStatusHistorySerializer
from rest_framework.pagination import PageNumberPagination
from django.db.models import Count
from collections import Counter
from datetime import datetime
from django.db import transaction
from django.db.models import F


class MachineListApiView(APIView):

    def post(self, request, *args, **kwargs):

        data = dict()
        data["name"] = request.data.get('name')

        serializer = MachineSerializer(data=data)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class IssueListApiView(APIView):

    def post(self, request, *args, **kwargs):

        data = dict()
        data["machine"] = request.data.get('machine_id')
        data["title"] = request.data.get('issue')
        data["description"] = request.data.get('description')
        data["status"] = request.data.get('Open')

        serializer = IssueSerializer(data=data)

        if serializer.is_valid():
            issue = serializer.save()
            history_entry = IssueStatusHistory(
                issue=issue,
                status=issue.status,
                timestamp=datetime.now(),
                comment=request.data.get('comment', '')
            )
            history_entry.save()

            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class IssueListPagination(PageNumberPagination):
    page_size = 10  # Set your preferred page size here
    page_size_query_param = 'page_size'
    max_page_size = 100

class AllIssueListApiView(generics.ListAPIView):
    queryset = Issue.objects.all()
    serializer_class = IssueSerializer
    pagination_class = IssueListPagination

class IssueListView(generics.ListCreateAPIView):

    serializer_class = IssueSerializer
    pagination_class = IssueListPagination

    def get_queryset(self):
        queryset = Issue.objects.all()

        machine_id = self.request.query_params.get('machine_id')
        if machine_id:
            queryset = queryset.filter(machine_id=machine_id)

        title = self.request.query_params.get('title')
        if title:
            queryset = queryset.filter(title__icontains=title)

        start_timestamp = self.request.query_params.get('start_timestamp')
        end_timestamp = self.request.query_params.get('end_timestamp')
        if start_timestamp and end_timestamp:
            queryset = queryset.filter(timestamp__gte=start_timestamp, timestamp__lte=end_timestamp)

        status = self.request.query_params.get('status')
        if status:
            real_status=None
            if status == "Open":
                real_status = 0
            elif status == "Resolved":
                real_status = 1
            elif status == "Urgent":
                real_status = 2
            elif status == "Close":
                real_status = 3
            queryset = queryset.filter(status=real_status)

        return queryset

class IssueReportsPerMachine(APIView):
    def get(self, request, format=None):
        issue_counts = Issue.objects.values('machine__id').annotate(issue_count=Count('id'))
        data = [{'machine_id': item['machine__id'], 'issue_count': item['issue_count']} for item in issue_counts]

        return Response(data, status=status.HTTP_200_OK)
    
class TopCommonWords(APIView):
    def get(self, request, format=None):
        issue_reports = Issue.objects.all()
        titles = [issue.title for issue in issue_reports]
        descriptions = [issue.description for issue in issue_reports]
        text_data = ' '.join(titles + descriptions).replace('.', '').replace(',', '')
        words = text_data.split()
        word_count = Counter(words)
        top_k = int(request.query_params.get('top_k', 5))
        top_words = self.get_top_k_common_words(word_count.items(), top_k)
        return Response(top_words, status=status.HTTP_200_OK)
    
    def get_top_k_common_words(self, word_tuples, top_k):
        return sorted(word_tuples,reverse=True,  key=lambda item: item[1])[:top_k]

class ResolveIssue(APIView):
    def get(self, request, issue_id, *args, **kwargs):

        issue = Issue.objects.get(pk=issue_id)
        issue_serializer = IssueSerializer(issue)
        issue_history = IssueStatusHistory.objects.filter(issue = issue_id)
        history_serializer = IssueStatusHistorySerializer(issue_history, many=True)
        response_data = issue_serializer.data 
        response_data["history "] = history_serializer.data

        return Response(response_data, status=status.HTTP_200_OK)
    
     
    def put(self, request, issue_id):

        try:
            issue = Issue.objects.select_for_update().get(pk=issue_id)
        except Issue.DoesNotExist:
            return Response({'error': 'Issue not found'}, status=status.HTTP_404_NOT_FOUND)
        
        if issue.status == 1:
            return Response({'error': 'Issue is already resolved'}, status=status.HTTP_400_BAD_REQUEST)
        
        status_issue = request.data.get('status')
        real_status=None
        if status_issue:
            if status_issue == "Open":
                real_status = 0
            elif status_issue == "Resolved":
                real_status = 1
            elif status_issue == "Urgent":
                real_status = 2
            elif status_issue == "Close":
                real_status = 3

            issue.status = real_status
            with transaction.atomic():
                issue.status = real_status
                issue.save()

        else:
            return Response({'error': 'Issue is not status'}, status=status.HTTP_400_BAD_REQUEST)
        
        history_entry = IssueStatusHistory(
            issue=issue,
            status=real_status,
            timestamp=datetime.now(),
            comment=request.data.get('comment', '')
        )
        history_entry.save()

        try:
            issue_history = IssueStatusHistory.objects.filter(issue=issue_id)
        except IssueStatusHistory.DoesNotExist:
            return Response({'error': 'Issue history not found'}, status=status.HTTP_404_NOT_FOUND)
        
        issue_serializer = IssueSerializer(issue)
        history_serializer = IssueStatusHistorySerializer(issue_history, many=True)
        response_data = issue_serializer.data 
        response_data["history "] = history_serializer.data

        return Response(response_data, status=status.HTTP_200_OK)
    

    
