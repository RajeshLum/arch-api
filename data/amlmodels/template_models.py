from django.db import models
from django.contrib.auth.models import User

class TemplateTitle(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="template_titles")
    title = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

    class Meta:
        db_table = "template_titles"
        verbose_name_plural = "Template Titles"

class TemplatePage(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="template_pages")
    template_title = models.ForeignKey(TemplateTitle, on_delete=models.CASCADE, related_name="pages")
    page_title = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.page_title

    class Meta:
        db_table = "template_pages"
        verbose_name_plural = "Template Pages"

class TemplateQuestion(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="template_questions")
    template_page = models.ForeignKey(TemplatePage, on_delete=models.CASCADE, related_name="questions")
    question = models.TextField()
    required = models.BooleanField(default=False)
    answer_type = models.CharField(max_length=50)
    options = models.JSONField(blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    description_enabled = models.BooleanField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.question

    class Meta:
        db_table = "template_questions"
        verbose_name_plural = "Template Questions"
