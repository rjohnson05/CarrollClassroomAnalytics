from rest_framework.response import Response
from rest_framework.decorators import api_view

from api import services

import logging
import pandas as pd

logger = logging.getLogger("views")


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

    @param request: HTTP request object
    @return: HTTP response object containing a dictionary of all the buildings currently holding classes
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


@api_view(["GET"])
def get_classroom_data(request):
    classroom_name = request.GET.get("classroom")
    logger.info(f"views.get_classroom_data: Classroom Name: {classroom_name}")
    courses = services.get_classroom_courses(classroom_name)
    logger.debug(f"get_classroom_data: Found courses held in {classroom_name}: {courses}")
    return Response(courses)


# @api_view(["POST"])
# def upload_file(request):
#     data_type = request.POST['dataType']
#     file = request.FILES['file']
#     df = pd.read_excel(file)
#     logger.debug(f"Uploaded File: {df}")
#     if data_type == "schedule":
#         services.upload_schedule_data(df)
#     else:
#         services.upload_classroom_data(df)
#
#     return Response({"message": "File uploaded"})
