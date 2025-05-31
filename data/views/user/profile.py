import logging

from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication

from data.models import Profile
from data.serializers.profile import ProfileSerializer

logger = logging.getLogger('django')

class ProfileView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            info, _ = Profile.objects.select_related('user').get_or_create(user=request.user)
            serializer = ProfileSerializer(info)
        
            response_data = {
                "user": {
                    "id": request.user.id,
                    "username": request.user.username,
                    "email": request.user.email,
                    "first_name": request.user.first_name,
                    "last_name": request.user.last_name,
                },
                "info": serializer.data,
            }

            return Response(response_data, status=status.HTTP_200_OK)
        
        except Exception as e:
            return Response(
                {"message": "Failed to retrieve profile."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
		
    def patch(self, request):
        user = request.user
        data = request.data
        files = request.FILES
          
        try:
            info, _ = Profile.objects.get_or_create(user=request.user)

            # Update User fields if provided
            first_name = data.get("first_name")
            last_name = data.get("last_name")
            email = data.get("email")

            updated = False

            if first_name:
                user.first_name = first_name
                updated = True
            if last_name:
                user.last_name = last_name
                updated = True
            if email:
                user.email = email
                updated = True

            if updated:
                user.save()
            
            # Update Profile fields
            photo = files.get('photo')
            serializer = ProfileSerializer(info, data=request.data, partial=True)
            if serializer.is_valid():
                if photo:
                    serializer.save(photo=photo)
                else:
                    serializer.save()
                
                # return Response(serializer.data)
                return Response(
                    {"message": "Profile updated successfully."},
                    status=status.HTTP_200_OK
                )
            
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        except Exception as e:
            return Response(
                {"message": "Failed to update profile."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
