import logging

from rest_framework.decorators import api_view
from rest_framework.request import Request
from rest_framework.response import Response

from api import services

logger = logging.getLogger("api_views")

"""
Contains the backend views for the Carroll College analytics software. Each of these views contains logic and make
queries fo the database. These methods receive HTTP requests and return a response to the front end.

Author: Ryan Johnson
"""


@api_view(["GET"])
def get_number_classes(request: Request) -> Response:
    """
    Queries the number of classrooms being used during each time block and then stores this information in a dictionary.
    Returns an HTTP request containing two dictionaries, the first of which containing the time blocks and the second
    containing the recently calculated number of classrooms used during each time block.

    :param request: HTTP request object containing the list of buildings in which to search for used classrooms
    :return: HTTP response object containing an array with two dictionaries: the first storing the time blocks and the
             second storing the number of used classrooms during each time block
    """
    buildings = request.GET.getlist("buildings[]")
    if buildings.__len__() == 0:
        # Get data for all buildings campus-wide
        number_classes = services.calculate_number_classes()
        logger.debug(f"get_number_classes - Calculated class numbers for all-campus: {number_classes}")
    else:
        # Get data for only specified buildings
        number_classes = services.calculate_number_classes(buildings)
        logger.debug(f"get_building_classes - Calculated class numbers for {buildings}: {number_classes}")
    return Response(number_classes)


@api_view(["GET"])
def get_building_names(request: Request) -> Response:
    """
    Returns a dictionary of all buildings holding classes that are currently in the database. The keys in this
    dictionary are the four-letter abbreviations for the building, while the values are the full names for the buildings.

    :param request: HTTP request object
    :return: HTTP response object containing a dictionary of all the buildings currently holding classes
    """
    buildings_list = services.get_all_buildings()
    logger.debug(f"get_building_names - Buildings list: {buildings_list}")
    return Response(buildings_list)


@api_view(["GET"])
def get_used_classrooms(request: Request) -> Response:
    """
    Used for listing all classrooms used during a specific time block. Returns a dictionary of all classrooms and their
    corresponding data that are used within a specified time block.

    :param request: HTTP request object containing the desired day, start/end times, and buildings in which to search for used classrooms
    :return: HTTP response object containing a dictionary of all the classrooms and their data that are used within a specified time block
    """
    day = request.GET.get("day")
    start_time = request.GET.get("startTime")
    end_time = request.GET.get("endTime")
    buildings = request.GET.get("buildings")
    if buildings == "":
        # Get data for all buildings campus-wide
        used_classrooms = services.get_used_classrooms(day, start_time, end_time)
        logger.debug(f"get_used_classrooms - Found used classrooms across all-campus: {used_classrooms}")
    else:
        buildings_list = buildings.split(", ")
        # Get data for only specified buildings
        used_classrooms = services.get_used_classrooms(day, start_time, end_time, buildings_list)
        logger.debug(f"get_used_classrooms - Found used classrooms for {buildings_list}: {used_classrooms}")

    return Response(used_classrooms)


@api_view(["GET"])
def get_classroom_data(request: Request) -> Response:
    """
    Used for displaying the weekly schedule for a single classroom. Returns a list containing two dictionaries, the
    first storing time blocks and the second the courses running during those time blocks.

    :param request: HTTP request object containing the classroom name to find data for
    :return: HTTP response object containing a list of time blocks and courses running during those time blocks for a single classroom
    """
    classroom_name = request.GET.get("classroom")
    courses = services.get_classroom_courses(classroom_name)
    logger.debug(f"get_classroom_data - Found courses held in {classroom_name}: {courses}")
    return Response(courses)


@api_view(["POST"])
def upload_file(request: Request) -> Response:
    """
    Creates model objects using the data from a file and moves them into the database.

    :param request: HTTP request object containing the data file and the type of file being uploaded
    :return: HTTP response object containing a boolean specifying whether the upload was successful and a list of any
             missing columns in the .csv file. If the upload is successful, the missing columns is a NoneType.
    """
    data_type = request.POST['dataType']
    file = request.FILES['file']

    if data_type == "schedule":
        # Handles schedule data .csv file uploads
        success_message = services.upload_schedule_data(file)
    else:
        # Handles classroom data .csv file uploads
        success_message = services.upload_classroom_data(file)

    success = success_message[0]
    missing_columns = success_message[1]

    logger.debug(f"upload_file - Upload Status: {success}, Missing Columns: {missing_columns}, File Name: {file.name}")
    return Response({"success": success, "missingColumns": missing_columns})


@api_view(["GET"])
def get_next_time(request: Request) -> Response:
    """
    Given the start time of a time block, finds the corresponding end time for the block. Used for paging when viewing
    the used classrooms for a specific time block, displaying the next time block.

    :param request: HTTP request object containing the day, start time, and building list for the desired block
    :return: HTTP response object containing the end time for the specified time block
    """
    day = request.GET.get("day")
    start_time = request.GET.get("currentEndTime")
    buildings = request.GET.get("buildings")
    buildings_list = buildings.split(", ")
    if buildings.__len__() == 0:
        next_end_time = services.get_next_time(day, start_time)
        logger.debug(
            f"get_next_time - End time for block starting at {start_time} on {day} (in all buildings): {next_end_time}")
    else:
        next_end_time = services.get_next_time(day, start_time, buildings_list)
        logger.debug(
            f"get_next_time - End time for block starting at {start_time} on {day} (in {buildings_list}): {next_end_time}")

    return Response(next_end_time)


@api_view(["GET"])
def get_past_time(request: Request) -> Response:
    """
    Given the end time of a time block, finds the corresponding start time for the block. Used for paging when viewing
    the used classrooms for a specific time block, displaying the previous time block.

    :param request: HTTP request object containing the day, end time, and building list for the desired block
    :return: HTTP response object containing the start time for the specified time block
    """
    day = request.GET.get("day")
    end_time = request.GET.get("currentStartTime")
    buildings = request.GET.get("buildings")
    buildings_list = buildings.split(", ")
    if buildings.__len__() == 0:
        past_start_time = services.get_past_time(day, end_time)
        logger.debug(f"get_past_time - Start time for block ending at {end_time} on {day} (in all buildings): "
                     f"{past_start_time}")
    else:
        past_start_time = services.get_past_time(day, end_time, buildings_list)
        logger.debug(f"get_past_time - Start time for next block ending at {end_time} on {day} "
                     f"(in {buildings_list}): {past_start_time}")

    return Response(past_start_time)
