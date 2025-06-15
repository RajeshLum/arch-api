from rest_framework import serializers
from data.amlmodels.template_models import TemplateTitle, TemplatePage, TemplateQuestion

class TemplateQuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = TemplateQuestion
        exclude = ('user', 'template_page', 'created_at', 'updated_at')

class TemplatePageSerializer(serializers.ModelSerializer):
    questions = TemplateQuestionSerializer(many=True)

    class Meta:
        model = TemplatePage
        exclude = ('user', 'template_title', 'created_at', 'updated_at')

class TemplateTitleSerializer(serializers.ModelSerializer):
    pages = TemplatePageSerializer(many=True)

    class Meta:
        model = TemplateTitle
        exclude = ('user', 'created_at', 'updated_at')
