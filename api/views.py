from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import api_view


@api_view(["GET"])
def get_number_classes(request):
    """
    Returns the number of classrooms being utilized during a specified time period.
    """
    start_time = request.query_params['start_time']
    end_time = request.query_params['end_time']
    return Response({'message': 'New Incoming Data'})
