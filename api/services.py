from api.models import Course, Classroom
import logging

logger = logging.getLogger("services")


def calculate_time_blocks(buildings) -> []:
    """
    Given a set of buildings, calculates every block of time in which there could be a different number of utilized
    classrooms and then returns this information in a dictionary. This dictionary uses the abbreviation for every
    weekday ('M', 'T', etc.) as the keys and an array of arrays as the values. Each of these value arrays contains
    many sub-arrays containing the start and end times for the block. If no time blocks are found for the specified
    buildings, an empty dictionary is returned.

    :param  buildings        List of buildings to look within for possible time blocks
    :return all_time_blocks  Dictionary containing every possible time block in which there could be a different
    number of utilized classrooms
    """
    all_times = []
    days_list = ['M', 'T', 'W', 'th', 'F']
    building_time_blocks = {}
    for day in days_list:
        if buildings == 'all':
            # Finds all start/end times on the current day and converts them from datetime objects to strings
            start_times = [time[0].strftime("%H:%M:%S") for time in
                           Course.objects.filter(day__contains=day).values_list(
                               'start_time').distinct()]
            end_times = [time[0].strftime("%H:%M:%S") for time in
                         Course.objects.values_list('end_time').filter(day__contains=day).distinct()]
        else:
            # Finds all start/end times in the specified building on the current day
            start_times = [time[0].strftime("%H:%M:%S") for time in
                           Course.objects.filter(classroom__building__in=buildings, day__contains=day).values_list(
                               'start_time').distinct()]
            end_times = [time[0].strftime("%H:%M:%S") for time in
                         Course.objects.values_list('end_time').filter(classroom__building__in=buildings,
                                                                       day__contains=day).distinct()]
        # all_times.append(start_times + end_times + ['6:00:00', '21:15:00'])
        all_times = start_times + end_times + ['06:00:00', '23:59:00']
        start_end_times = sorted(set(all_times))  # Organizes times from earliest to latest
        logger.debug(f"calculate_time_blocks: Possible Start/End Times: {start_end_times}")
        time_blocks = []  # Stores the time block tuples for a given day

        if len(start_end_times) > 0:
            # Group the time blocks together
            for i in range(0, len(start_end_times) - 1):
                time_block = [start_end_times[i], start_end_times[i + 1]]
                time_blocks.append(time_block)
            building_time_blocks[day] = time_blocks
            logger.debug(f"List of Time Blocks for {buildings}: {building_time_blocks}")
    return building_time_blocks


def calculate_number_classes(buildings='all'):
    """
    Queries the number of courses running during each time block and then stores this information in a dictionary.
    Returns an array containing two dictionaries, the first of which containing the time blocks in which a course is
    running inside the specified building and the second containing the recently calculated number of courses running
    during each time block.

    :param buildings: Specifies which building(s) to return the number of courses for ('all' includes all
    buildings)
    :return [time_blocks, all_num_classes] Array holding two dictionaries, the first storing time blocks
    and the second the number of courses running during those time blocks
    """
    time_blocks = calculate_time_blocks(buildings)
    if not time_blocks:
        logger.debug(f"calculate_number_classes: No time blocks found for {buildings}")
        return [{}, {}]
    all_num_classes = {}  # Dictionary to hold ALL the class number data
    for day, day_block_list in time_blocks.items():
        day_num_classes = {}  # Dictionary to hold the class number data for a single day
        for block in day_block_list:
            block_start_time = block[0]
            block_end_time = block[1]
            if buildings == 'all':
                # Counts the number of courses (campus-wide) running between the current block's start/end times
                block_num_classes = Course.objects.all().filter(day__contains=day,
                                                                start_time__lte=block_start_time,
                                                                end_time__gte=block_end_time)
            else:
                # Counts the number of courses (within specified buildings) running between the current block's
                # start/end times
                block_num_classes = Course.objects.all().filter(day__contains=day,
                                                                start_time__lte=block_start_time,
                                                                end_time__gte=block_end_time,
                                                                classroom__building__in=buildings)
            # Account for the possibility of several courses in a single classrooms by only counting the unique
            # classrooms in use
            unique_classrooms = []
            for course in block_num_classes:
                if course.classroom.name not in unique_classrooms:
                    unique_classrooms.append(course.classroom.name)

            day_num_classes[block_start_time] = len(unique_classrooms)
        logger.debug(f"calculate_number_classes: Number of classes for time blocks during {day}: {day_num_classes}")
        all_num_classes[day] = day_num_classes
    logger.debug(f"calculate_number_classes: Number of classes calculated for time blocks in {buildings}")
    return [time_blocks, all_num_classes]


def get_all_buildings():
    """
    Returns a dictionary storing the names of all buildings in the current list of courses.
    """
    buildings_list = Classroom.BUILDINGS
    return buildings_list


def get_used_classrooms(day: str, start_time: str, end_time: str, buildings: str = "all") -> []:
    """
    Returns a list of all classrooms used during a specified time block and data about the course being held in the
    classroom during the specified time block.
    """
    if buildings == 'all':
        current_courses = Course.objects.all().filter(day__contains=day,
                                                      start_time__lte=start_time,
                                                      end_time__gte=end_time)
    else:
        current_courses = Course.objects.all().filter(day__contains=day,
                                                      start_time__lte=start_time,
                                                      end_time__gte=end_time,
                                                      classroom__building__in=buildings)

    courses_data = [[course.name, course.classroom.name, course.instructor, course.classroom.occupancy, course.enrollment]
                    for course in current_courses]

    classrooms_dict = {}
    for course_data in courses_data:
        classroom = course_data.pop(1)
        if classroom not in classrooms_dict.keys():
            classrooms_dict[classroom] = course_data
        else:
            classrooms_dict[classroom] += course_data

    return classrooms_dict
