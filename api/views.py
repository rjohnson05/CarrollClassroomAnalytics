from rest_framework.response import Response
from rest_framework.decorators import api_view
from api.models import Course


@api_view(["GET"])
def get_number_classes(request):
    """
    Queries the number of courses running during each time block and then stores this information in a dictionary.
    Returns an HTTP request containing two dictionaries, the first of which containing the time blocks and the second
    containing the recently calculated number of courses running during each time block.

    :param request: HTTP request object
    :return: HTTP response object containing an array with two dictionaries: time_blocks and all_num_classes
    """
    time_blocks = get_time_blocks()
    all_num_classes = {}  # Dictionary to hold ALL the class number data
    for day, day_block_list in time_blocks.items():
        day_num_classes = {}  # Dictionary to hold the class number data for a single day
        for block in day_block_list:
            block_start_time = block[0]
            block_end_time = block[1]
            # Counts the number of courses running between the current block's start/end times
            block_num_classes = Course.objects.all().filter(start_time__gte=block_start_time,
                                                            end_time__gte=block_end_time)
            day_num_classes[block_start_time] = len(block_num_classes)
        all_num_classes[day] = day_num_classes
    return Response([time_blocks, all_num_classes])


def get_time_blocks():
    """
    Calculates every block of time in which there could be a different number of utilized classrooms and then returns
    this information in a dictionary. This dictionary uses the abbreviation for every weekday ('M', 'T', etc.) as the
    keys and an array of arrays as the values. Each of these value arrays contains many sub-arrays containing the
    start and end times for the block.

    :return: all_time_blocks  Dictionary containing every possible time block in which there could be a different
    number of utilized classrooms
    """
    days_list = ['M', 'T', 'W', 'th', 'F']
    all_time_blocks = {}
    for day in days_list:
        # Finds all start/end times on the current day and converts them from datetime objects to strings
        start_times = [time[0].strftime("%H:%M:%S") for time in
                       Course.objects.filter(day__contains=day).values_list('start_time').distinct()]
        end_times = [time[0].strftime("%H:%M:%S") for time in
                     Course.objects.values_list('end_time').filter(day__contains=day).distinct()]
        start_end_times = sorted(start_times + end_times)  # Organizes times from earliest to latest
        time_blocks = []  # Stores the time block tuples for a given day
        if len(start_end_times) > 0:
            for i in range(0, len(start_end_times) - 1):
                time_block = [start_end_times[i], start_end_times[i + 1]]
                time_blocks.append(time_block)
            all_time_blocks[day] = time_blocks
    return all_time_blocks
