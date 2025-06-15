from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from rest_framework.pagination import PageNumberPagination
from django.shortcuts import get_object_or_404
from django.db import transaction

from data.amlmodels.template_models import TemplateTitle, TemplatePage, TemplateQuestion
from data.serializers.template_serializers import TemplateTitleSerializer

class TemplateTitleListCreateView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        if request.user.is_staff:
            queryset = TemplateTitle.objects.all().order_by('-created_at')
        else:
            queryset = TemplateTitle.objects.filter(user=request.user).order_by('-created_at')

        paginator = PageNumberPagination()
        paginator.page_size = 10
        paginated_queryset = paginator.paginate_queryset(queryset, request)
        if paginated_queryset is None:
            return Response({'message': 'Pagination failed.'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        serializer = TemplateTitleSerializer(paginated_queryset, many=True)
        return paginator.get_paginated_response(serializer.data)

    def camel_to_snake(self, s):
        import re
        return re.sub(r'(?<!^)(?=[A-Z])', '_', s).lower()

    def normalize_page(self, page):
        # Accept both camelCase and snake_case
        return {
            'id': page.get('id'),
            'page_title': page.get('page_title') or page.get('pageTitle'),
            'questions': [self.normalize_question(q) for q in page.get('questions', [])]
        }

    def normalize_question(self, q):
        return {
            'id': q.get('id'),
            'question': q.get('question'),
            'answer_type': q.get('answer_type') or q.get('answerType'),
            'required': q.get('required'),
            'description_enabled': q.get('description_enabled') if 'description_enabled' in q else q.get('descriptionEnabled'),
            'description': q.get('description'),
            'options': q.get('options')
        }

    @transaction.atomic
    def post(self, request):
        data = request.data.copy()
        # Normalize pages/questions to snake_case
        if 'pages' in data:
            data['pages'] = [self.normalize_page(p) for p in data['pages']]
        serializer = TemplateTitleSerializer(data=data)
        if serializer.is_valid():
            pages_data = serializer.validated_data.pop('pages', [])
            template_title = serializer.save(user=request.user)
            for page_data in pages_data:
                questions_data = page_data.pop('questions', [])
                page = TemplatePage.objects.create(
                    user=request.user,
                    template_title=template_title,
                    page_title=page_data.get('page_title', ''),
                )
                for question_data in questions_data:
                    TemplateQuestion.objects.create(
                        user=request.user,
                        template_page=page,
                        question=question_data.get('question'),
                        description=question_data.get('description', ''),
                        answer_type=question_data.get('answer_type', ''),
                        required=question_data.get('required', False),
                        options=question_data.get('options', None),
                        description_enabled=question_data.get('description_enabled', False),
                    )
            result = TemplateTitleSerializer(template_title)
            return Response(result.data, status=status.HTTP_201_CREATED)
        # DEBUG: Return serializer errors for diagnosis
        import logging
        logging.error(f"TemplateTitleSerializer errors: {serializer.errors}")
        return Response({"errors": serializer.errors, "data": data}, status=status.HTTP_400_BAD_REQUEST)

class TemplateTitleDetailView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    @staticmethod
    def normalize_page(page):
        return {
            'id': page.get('id'),
            'page_title': page.get('page_title') or page.get('pageTitle'),
            'questions': [TemplateTitleDetailView.normalize_question(q) for q in page.get('questions', [])]
        }

    @staticmethod
    def normalize_question(q):
        return {
            'id': q.get('id'),
            'question': q.get('question'),
            'answer_type': q.get('answer_type') or q.get('answerType'),
            'required': q.get('required'),
            'description_enabled': q.get('description_enabled') if 'description_enabled' in q else q.get('descriptionEnabled'),
            'description': q.get('description'),
            'options': q.get('options')
        }

    def get_template_title(self, pk, user):
        if user.is_staff:
            return get_object_or_404(TemplateTitle, pk=pk)
        return get_object_or_404(TemplateTitle, pk=pk, user=user)

    def get(self, request, pk):
        obj = self.get_template_title(pk, request.user)
        serializer = TemplateTitleSerializer(obj)
        return Response(serializer.data)

    @transaction.atomic
    def patch(self, request, pk):
        return self._update(request, pk, partial=True)

    @transaction.atomic
    def put(self, request, pk):
        return self._update(request, pk, partial=False)

    def _update(self, request, pk, partial):
        obj = self.get_template_title(pk, request.user)
        update_data = request.data.copy()
        # Normalize pages/questions to snake_case
        if 'pages' in update_data:
            update_data['pages'] = [self.normalize_page(p) for p in update_data['pages']]
        serializer = TemplateTitleSerializer(obj, data=update_data, partial=partial)
        if serializer.is_valid():
            pages_data = serializer.validated_data.pop('pages', [])
            template_title = serializer.save()
            existing_pages = {page.id: page for page in template_title.pages.all()}
            sent_page_ids = set()
            for page_data in pages_data:
                page_id = page_data.get('id')
                questions_data = page_data.pop('questions', [])
                if page_id and page_id in existing_pages:
                    page = existing_pages[page_id]
                    page.page_title = page_data.get('pageTitle', page_data.get('page_title', page.page_title))
                    page.save()
                    sent_page_ids.add(page_id)
                else:
                    page = TemplatePage.objects.create(
                        user=template_title.user,
                        template_title=template_title,
                        page_title=page_data.get('pageTitle', page_data.get('page_title', '')),
                    )
                    sent_page_ids.add(page.id)
                # Handle questions for this page
                existing_questions = {q.id: q for q in page.questions.all()}
                sent_question_ids = set()
                for question_data in questions_data:
                    question_id = question_data.get('id')
                    if question_id and question_id in existing_questions:
                        q = existing_questions[question_id]
                        q.question = question_data.get('question', q.question)
                        q.description = question_data.get('description', q.description)
                        q.answer_type = question_data.get('answerType', question_data.get('answer_type', q.answer_type))
                        q.required = question_data.get('required', q.required)
                        q.options = question_data.get('options', q.options)
                        q.description_enabled = question_data.get('descriptionEnabled', q.description_enabled)
                        q.save()
                        sent_question_ids.add(question_id)
                    else:
                        q = TemplateQuestion.objects.create(
                            user=template_title.user,
                            template_page=page,
                            question=question_data.get('question'),
                            description=question_data.get('description', ''),
                            answer_type=question_data.get('answerType', question_data.get('answer_type', '')),
                            required=question_data.get('required', False),
                            options=question_data.get('options', None),
                            description_enabled=question_data.get('descriptionEnabled', False),
                        )
                        sent_question_ids.add(q.id)
                # Delete removed questions
                for qid, q in existing_questions.items():
                    if qid not in sent_question_ids:
                        q.delete()
            # Delete removed pages
            for page_id, page in existing_pages.items():
                if page_id not in sent_page_ids:
                    page.delete()
            result = TemplateTitleSerializer(template_title)
            return Response(result.data)
        # DEBUG: Return serializer errors for diagnosis
        import logging
        logging.error(f"TemplateTitleSerializer errors: {serializer.errors}")
        return Response({"errors": serializer.errors, "data": update_data}, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        obj = self.get_template_title(pk, request.user)
        obj.delete()
        return Response({'detail': 'Template title deleted successfully.'}, status=status.HTTP_204_NO_CONTENT)
