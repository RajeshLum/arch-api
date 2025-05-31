from rest_framework.views import APIView
from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination

from data.amlmodels.search_history_model import SearchHistory
from data.serializers.search_history_serializer import SearchHistorySerializer


class StandardResultsSetPagination(PageNumberPagination):
    """
    Standard pagination class for search history results
    """
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100

class SearchHistoryListCreateView(APIView):
    """
    API endpoint for listing and creating search history entries.
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request, *args, **kwargs):
        """
        List all search history for the current user with pagination.
        """
        user = request.user
        search_history = SearchHistory.objects.filter(user=user).order_by('-created_at')
        
        # Apply pagination
        paginator = StandardResultsSetPagination()
        page = paginator.paginate_queryset(search_history, request)
        
        if page is not None:
            serializer = SearchHistorySerializer(page, many=True)
            result = paginator.get_paginated_response(serializer.data)
            result.data['message'] = 'Search history retrieved successfully'
            return result
            
        # If page is None, return all results (should not happen with proper pagination)
        count = search_history.count()
        serializer = SearchHistorySerializer(search_history, many=True)
        return Response({
            'message': f'Successfully retrieved {count} search history items',
            'count': count,
            'data': serializer.data
        })
    
    def post(self, request, *args, **kwargs):
        """
        Create a new search history entry.
        """
        serializer = SearchHistorySerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            search_history = serializer.save()
            return Response({
                'message': 'Search history entry created successfully',
                'data': serializer.data
            }, status=status.HTTP_201_CREATED)
        return Response({
            'message': 'Failed to create search history entry',
            'errors': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)


class SearchHistoryDetailView(APIView):
    """
    API endpoint for retrieving, updating, and deleting a specific search history entry.
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def get_object(self, pk, user):
        """
        Helper method to get the object with given pk and user.
        """
        try:
            return SearchHistory.objects.get(pk=pk, user=user)
        except SearchHistory.DoesNotExist:
            return None
    
    def get(self, request, pk, *args, **kwargs):
        """
        Retrieve a search history entry.
        """
        search_history = self.get_object(pk, request.user)
        if not search_history:
            return Response({
                'message': 'Search history entry not found',
                'error': 'Not found'
            }, status=status.HTTP_404_NOT_FOUND)
            
        serializer = SearchHistorySerializer(search_history)
        return Response({
            'message': 'Search history entry retrieved successfully',
            'data': serializer.data
        })
    
    def put(self, request, pk, *args, **kwargs):
        """
        Update a search history entry.
        """
        search_history = self.get_object(pk, request.user)
        if not search_history:
            return Response({
                'message': 'Search history entry not found',
                'error': 'Not found'
            }, status=status.HTTP_404_NOT_FOUND)
            
        serializer = SearchHistorySerializer(search_history, data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response({
                'message': 'Search history entry updated successfully',
                'data': serializer.data
            })
        return Response({
            'message': 'Failed to update search history entry',
            'errors': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)
    
    def delete(self, request, pk, *args, **kwargs):
        """
        Delete a search history entry.
        """
        search_history = self.get_object(pk, request.user)
        if not search_history:
            return Response({
                'message': 'Search history entry not found',
                'error': 'Not found'
            }, status=status.HTTP_404_NOT_FOUND)
            
        search_history.delete()
        return Response({
            'message': 'Search history entry deleted successfully'
        }, status=status.HTTP_200_OK)


class SearchHistoryClearView(APIView):
    """
    API endpoint for clearing all search history for the current user.
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def delete(self, request, *args, **kwargs):
        """
        Clear all search history for the current user.
        """
        user = request.user
        deleted_count, _ = SearchHistory.objects.filter(user=user).delete()
        
        return Response({
            'message': f'Successfully deleted {deleted_count} search history items',
            'deleted_count': deleted_count
        }, status=status.HTTP_200_OK)


class RecentSearchHistoryView(APIView):
    """
    API endpoint for retrieving recent search history.
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request, *args, **kwargs):
        """
        Get the most recent search history items (limited to 10).
        """
        user = request.user
        recent_searches = SearchHistory.objects.filter(user=user).order_by('-created_at')[:10]
        count = len(recent_searches)
        serializer = SearchHistorySerializer(recent_searches, many=True)
        
        return Response({
            'message': f'Successfully retrieved {count} recent search history items',
            'count': count,
            'data': serializer.data
        })
