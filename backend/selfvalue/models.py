from django.db import models
# Create your models here.

from django.conf import settings


class SelfValueReport(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    report_text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    qa_history = models.JSONField(default=list, blank=True)

    def __str__(self):
        return f"SelfValueReport #{self.id}"
