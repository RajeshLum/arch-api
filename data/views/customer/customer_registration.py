from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from rest_framework.pagination import PageNumberPagination
from rest_framework_simplejwt.authentication import JWTAuthentication
from django.shortcuts import get_object_or_404

from data.models import Customer, Identity, Employability, BankInfo, CustomerAdditionalInfo, BusinessInfo
from data.serializers.customer import CustomerSerializer, IdentitySerializer, EmployabilitySerializer, BankInfoSerializer, CustomerAdditionalInfoSerializer, BusinessInfoSerializer

# list, add
class CustomerListCreateView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def save_customer_related_data(self, request_data, customer_instance):
        copied_data = request_data.copy()
        
        # identity
        if copied_data.get("id_number"):
            identity_data = copied_data
            identity_data['customer'] = customer_instance.id

            identity_serializer = IdentitySerializer(data=identity_data)
            if identity_serializer.is_valid():
                identity_serializer.save(customer=customer_instance)
            
        # employment
        if copied_data.get("status"):
            employment_data = copied_data
            employment_data['customer'] = customer_instance.id

            employment_serializer = EmployabilitySerializer(data=employment_data)
            if employment_serializer.is_valid():
                employment_serializer.save(customer=customer_instance)
            
        # bank info
        if copied_data.get("account_number"):
            bank_details = copied_data
            bank_details['customer'] = customer_instance.id

            bank_serializer = BankInfoSerializer(data=bank_details)
            if bank_serializer.is_valid():
                bank_serializer.save(customer=customer_instance)
            
        # additional information
        if copied_data.get("pep_status"):
            addi_info = copied_data
            addi_info['customer'] = customer_instance.id

            addi_serializer = CustomerAdditionalInfoSerializer(data=addi_info)
            if addi_serializer.is_valid():
                addi_serializer.save(customer=customer_instance)
            
        # business info
        if copied_data.get("business_name"):
            business_info = copied_data
            business_info['customer'] = customer_instance.id

            business_serializer = BusinessInfoSerializer(data=business_info)
            if business_serializer.is_valid():
                business_serializer.save(customer=customer_instance)
        
    def get1(self, request):
        """List all customers for the authenticated user (admin gets all)"""
        if request.user.is_staff:
            customers = Customer.objects.all()
        else:
            customers = Customer.objects.filter(user=request.user)
        
        serializer = CustomerSerializer(customers, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    def get2(self, request):
        if request.user.is_staff:
            queryset = Customer.objects.all().order_by('-id')
        else:
            queryset = Customer.objects.filter(user=request.user).order_by('-id')

        # Apply pagination manually
        paginator = PageNumberPagination()
        paginator.page_size = 20
        paginated_qs = paginator.paginate_queryset(queryset, request)

        serializer = CustomerSerializer(paginated_qs, many=True)
        return paginator.get_paginated_response(serializer.data)
    
    def get(self, request):
        # Get queryset based on user role
        if request.user.is_staff:
            queryset = Customer.objects.all()
        else:
            queryset = Customer.objects.filter(user=request.user)

        # Initialize paginator
        paginator = PageNumberPagination()
        paginator.page_size = 10
        
        paginated_queryset = paginator.paginate_queryset(queryset, request)

        # Safety check (but paginator should return a list, not None, if set up correctly)
        if paginated_queryset is None:
            return Response({"message": "Pagination failed."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
        # Serialize the paginated queryset
        serialized_data = CustomerSerializer(paginated_queryset, many=True).data
        
        # Return paginated response
        return paginator.get_paginated_response(serialized_data)
    
    def post(self, request):
        """Create a new customer for the authenticated user"""
        data = request.data.copy()
        data['user'] = request.user.id
        data['status'] = 'pending'

        serializer = CustomerSerializer(data=data)
        if serializer.is_valid():
            customer_instance = serializer.save(user=request.user)
            
            if customer_instance:
                self.save_customer_related_data(request.data, customer_instance)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CustomerDetailView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [permissions.IsAuthenticated]
    
    def update_customer_related_data(self, request_data, customer):
        copied_data = request_data.copy()
        
        # identity
        if copied_data.get("id_number"):
            identity = Identity.objects.filter(customer=customer).first()
            if identity:
                serializer = IdentitySerializer(identity, data=request_data, partial=True)
                if serializer.is_valid():
                    serializer.save()
                    
        # employment
        if copied_data.get("status"):
            employment = Employability.objects.filter(customer=customer).first()
            if employment:
                serializer = EmployabilitySerializer(employment, data=request_data, partial=True)
                if serializer.is_valid():
                    serializer.save()
                    
        # bank info
        if copied_data.get("account_number"):
            bank_info = BankInfo.objects.filter(customer=customer).first()
            if bank_info:
                serializer = BankInfoSerializer(bank_info, data=request_data, partial=True)
                if serializer.is_valid():
                    serializer.save()
                    
        # additional information
        if copied_data.get("pep_status"):
            addi_info = CustomerAdditionalInfo.objects.filter(customer=customer).first()
            if addi_info:
                serializer = CustomerAdditionalInfoSerializer(addi_info, data=request_data, partial=True)
                if serializer.is_valid():
                    serializer.save()
                    
        # business info
        if copied_data.get("business_name"):
            business_info = BusinessInfo.objects.filter(customer=customer).first()
            if business_info:
                serializer = BusinessInfoSerializer(business_info, data=request_data, partial=True)
                if serializer.is_valid():
                    serializer.save()
        

    def get_customer(self, pk, user):
        """Helper to get object ensuring user access"""
        if user.is_staff:
            return get_object_or_404(Customer, pk=pk)
        
        return get_object_or_404(Customer, pk=pk, user=user)

    def get(self, request, pk):
        """Retrieve a specific customer"""
        customer = self.get_customer(pk, request.user)
        serializer = CustomerSerializer(customer)
        
        final_response = {
            "customer": serializer.data,
        }
          
        customer_id = customer.id
        if customer_id is not None:
            identity = Identity.objects.filter(customer_id=customer_id).first()
            if identity:
                final_response["identity"] = IdentitySerializer(identity).data
            
            employability = Employability.objects.filter(customer_id=customer_id).first()
            if employability:
                final_response["employability"] = EmployabilitySerializer(employability).data
            
            bank_info = BankInfo.objects.filter(customer_id=customer_id).first()
            if bank_info:
                final_response["bank_info"] = BankInfoSerializer(bank_info).data
            
            customer_additional_info = CustomerAdditionalInfo.objects.filter(customer_id=customer_id).first()
            if customer_additional_info:
                final_response["customer_additional_info"] = CustomerAdditionalInfoSerializer(customer_additional_info).data
            
            business_info = BusinessInfo.objects.filter(customer_id=customer_id).first()
            if business_info:
                final_response["business_info"] = BusinessInfoSerializer(business_info).data
        
        return Response(final_response, status=status.HTTP_200_OK)

    def patch(self, request, pk):
        """Update a specific customer (partial update)"""
        customer = self.get_customer(pk, request.user)
        serializer = CustomerSerializer(customer, data=request.data, partial=True)
        
        if serializer.is_valid():
            files = request.FILES
            photo = files.get('photo')
                 
            if photo:
                serializer.save(photo=photo)
            else:
                serializer.save()

            self.update_customer_related_data(request.data, customer)
                
            return Response(serializer.data)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        """Delete a customer"""
        customer = self.get_customer(pk, request.user)
        customer.delete()
        
        return Response({"detail": "Customer deleted successfully."}, status=status.HTTP_204_NO_CONTENT)
 