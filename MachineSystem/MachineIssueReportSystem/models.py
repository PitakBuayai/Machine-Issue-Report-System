from django.db import models

# Create your models here.
class Machine(models.Model):
    name = models.CharField(max_length=255)
    def __str__(self):
        return f"{self.name}"

class Issue(models.Model):
    STATUS_CHOICES = (
        (0, "Open"),
        (1, "Resolved"),
        (2, "Urgent"),
        (3, "Close")
    )

    machine = models.ForeignKey(Machine, on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    description = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    status = models.IntegerField(choices=STATUS_CHOICES)


class IssueStatusHistory(models.Model):
    STATUS_CHOICES = (
        (0, "Open"),
        (1, "Resolved"),
        (2, "Urgent"),
        (3, "Close")
    )

    issue = models.ForeignKey(Issue, on_delete=models.CASCADE)
    status = models.IntegerField(choices=STATUS_CHOICES)
    timestamp = models.DateTimeField(auto_now_add=True)
    comment = models.TextField()