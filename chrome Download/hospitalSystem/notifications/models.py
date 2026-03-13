from django.db import models

class EmailLog(models.Model):
    email_type = models.CharField(max_length=50)
    recipient = models.EmailField()
    status = models.CharField(max_length=20, default='PENDING')
    sent_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.email_type} to {self.recipient} - {self.status}"
