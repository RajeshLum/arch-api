from django.db import models
from django.contrib.auth.models import User

class SearchHistory(models.Model):
    """
    Model to store user search history
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="search_history")
    query = models.CharField(max_length=255)
    result_count = models.IntegerField(default=0)
    filters = models.JSONField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.user.username} - {self.query}"

    class Meta:
        db_table = "search_history"
        verbose_name_plural = "Search Histories"
        ordering = ['-created_at']  # Most recent searches first
