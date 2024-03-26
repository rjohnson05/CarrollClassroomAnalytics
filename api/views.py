from django.shortcuts import render
from django.core import serializers
from django.core.serializers import serialize
from django.http import JsonResponse
from rest_framework.response import Response
from rest_framework.decorators import api_view
from api.models import Classroom, Instructor, Course
from api import services
from django.core import serializers
import logging
logger = logging.getLogger("views")

def get_classroom_data(request):
    classroom_data = list(Classroom.objects.values())
    return JsonResponse(classroom_data, safe=False)

def get_course_data(request):
    course_data = list(Course.objects.values())
    return JsonResponse(course_data, safe=False)

@api_view(["GET"])
def get_number_classes(request):
    """
    Queries the number of courses running during each time block and then stores this information in a dictionary.
    Returns an HTTP request containing two dictionaries, the first of which containing the time blocks and the second
    containing the recently calculated number of courses running during each time block.

    :param request: HTTP request object
    :return: HTTP response object containing an array with two dictionaries: time_blocks and all_num_classes
    """
    buildings = request.GET.getlist("buildings[]")
    number_classes = None
    if buildings.__len__() == 0:
        # Get data for all buildings campus-wide
        number_classes = services.calculate_number_classes()
        logger.debug(f"get_number_classes: Calculated class numbers for all-campus - {number_classes}")
    else:
        # Get data for only specified buildings
        number_classes = services.calculate_number_classes(buildings)
        logger.debug(f"get_building_classes: Calculated class numbers for {buildings} - {number_classes}")
    return Response(number_classes)





@api_view(["GET"])
def get_building_names(request):
    """
    Returns a dictionary of all buildings holding classes that are currently in the database. The keys in this
    dictionary are the four-letter abbreviations for the building, while the values are the full names for the buildings.

    :param request: HTTP request object
    :return: HTTP response object containing a dictionary of all the buildings currently holding classes
    """
    buildings_list = services.get_all_buildings()
    return Response(buildings_list)

@api_view(["GET"])
def get_used_classrooms(request):
    day = request.GET.get("day")
    start_time = request.GET.get("startTime")
    end_time = request.GET.get("endTime")
    buildings = request.GET.get("buildings")
    if buildings == "":
        # Get data for all buildings campus-wide
        used_classrooms = services.get_used_classrooms(day, start_time, end_time)
        logger.debug(f"get_used_classrooms: Found used classrooms across all-campus - {used_classrooms}")
    else:
        buildings_list = buildings.split(",")
        # Get data for only specified buildings
        used_classrooms = services.get_used_classrooms(day, start_time, end_time, buildings_list)
        logger.debug(f"get_used_classrooms: Found used classrooms for {buildings_list} - {used_classrooms}")

    return Response(used_classrooms)
