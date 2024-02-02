from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import api_view


@api_view(["GET"])
def home(request):
    """
    Currently returns a random text message for display on the home page
    """
    return Response({'message': 'New Incoming Data'})
