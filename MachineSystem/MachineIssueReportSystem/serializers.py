from rest_framework import serializers
from .models import Machine, Issue, IssueStatusHistory
class MachineSerializer(serializers.ModelSerializer):
    class Meta:
        model = Machine
        fields = ["name"]

class StatusField(serializers.Field):

    def to_representation(self, obj):
        status_mapping = {0: "Open", 1: "Resolved", 2: "Urgent", 3:"Close"}
        return status_mapping[obj]

    def to_internal_value(self, data):
        if data == "Open":
            return 0
        elif data == "Resolved":
            return 1
        elif data == "Urgent":
            return 2
        elif data == "Close":
            return 3
        raise serializers.ValidationError("Invalid status value")

class IssueSerializer(serializers.ModelSerializer):
    status = StatusField()

    class Meta:
        model = Issue
        fields = ['machine', 'title','description', 'timestamp','status']

class IssueStatusHistorySerializer(serializers.ModelSerializer):
    status = StatusField()

    class Meta:
        model = IssueStatusHistory
        fields = ['issue', 'status', 'timestamp','comment']




