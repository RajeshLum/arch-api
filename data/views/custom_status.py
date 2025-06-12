from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from rest_framework.pagination import PageNumberPagination
from django.shortcuts import get_object_or_404

from data.amlmodels.custom_status_models import CustomStatus
from data.serializers.custom_status import CustomStatusSerializer
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from rest_framework.pagination import PageNumberPagination
from django.shortcuts import get_object_or_404

class CustomStatusListCreateView(APIView):
    """
    API view to list all custom statuses or create a new one.
    """
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        if request.user.is_staff:
            queryset = CustomStatus.objects.all().order_by('-created_at')
        else:
            queryset = CustomStatus.objects.filter(user=request.user).order_by('-created_at')

        serializer = CustomStatusSerializer(queryset, many=True)
        return Response(serializer.data)

    def post(self, request):
        data = request.data.copy()
        label = data.get('label', '')
        serializer = CustomStatusSerializer(data=data)
        if serializer.is_valid():
            instance = serializer.save(user=request.user)
            instance.value = label.lower().replace(' ', '_') if label else ''
            instance.save()
            return Response(CustomStatusSerializer(instance).data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class CustomStatusDetailView(APIView):
    """
    API view to retrieve, update or delete a custom status.
    """
    permission_classes = [permissions.IsAuthenticated]

    def get_custom_status(self, pk, user):
        if user.is_staff:
            return get_object_or_404(CustomStatus, pk=pk)
        return get_object_or_404(CustomStatus, pk=pk, user=user)

    def get(self, request, pk):
        obj = self.get_custom_status(pk, request.user)
        serializer = CustomStatusSerializer(obj)
        return Response(serializer.data)

    def patch(self, request, pk):
        obj = self.get_custom_status(pk, request.user)
        update_data = request.data.copy()
        if 'user' in update_data:
            del update_data['user']
        serializer = CustomStatusSerializer(obj, data=update_data, partial=True)
        if serializer.is_valid():
            instance = serializer.save()
            if 'label' in update_data:
                instance.value = update_data['label'].lower().replace(' ', '_')
                instance.save()
            return Response(CustomStatusSerializer(instance).data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        obj = self.get_custom_status(pk, request.user)
        obj.delete()
        return Response({"detail": "Custom status deleted successfully."}, status=status.HTTP_204_NO_CONTENT)
