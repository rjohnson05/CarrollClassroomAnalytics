import logging
import re
from datetime import datetime

import pandas as pd

from api.models import Course, Classroom, Instructor

logger = logging.getLogger("services")

"""
Contains all business logic for the Carroll College classroom analytics software. Conducts all database queries and 
returns the results to the corresponding view.

Author: Ryan Johnson
"""


def calculate_time_blocks(buildings):
    """
    Given a set of buildings, calculates every block of time in which there could be a different number of utilized
    classrooms and then returns this information in a dictionary. This dictionary uses the abbreviation for every
    weekday ('M', 'T', etc.) as the keys and an array of arrays as the values. Each of these value arrays contains
    many sub-arrays containing the start and end times for the block. If no time blocks are found for the specified
    buildings, an empty dictionary is returned.

    :param  buildings:       list of buildings to look within for possible time blocks
    :return                  dictionary containing every possible time block in which there could be a different
                             number of utilized classrooms
    """
    days_list = ['M', 'T', 'W', 'th', 'F']
    building_time_blocks = {}
    for day in days_list:
        if buildings == 'all':
            # Finds all start/end times on the current day from ALL buildings and converts them from datetime objects
            # to strings
            start_times = [time[0].strftime("%H:%M:%S") for time in
                           Course.objects.filter(day__contains=day).values_list(
                               'start_time').distinct().exclude(start_time__isnull=True).exclude(
                               classroom__building__in=["Unknown", "OFCP"])]
            end_times = [time[0].strftime("%H:%M:%S") for time in
                         Course.objects.values_list('end_time').filter(day__contains=day).distinct()
                         .exclude(end_time__isnull=True).exclude(classroom__building__in=["Unknown", "OFCP"])]
        else:
            # Finds all start/end times in the specified building on the current day
            start_times = [time[0].strftime("%H:%M:%S") for time in
                           Course.objects.all().filter(classroom__building__in=buildings, day__contains=day).
                           values_list('start_time').distinct().exclude(start_time__isnull=True)
                           .exclude(classroom__building__in=["Unknown", "OFCP"])]
            end_times = [time[0].strftime("%H:%M:%S") for time in
                         Course.objects.all().filter(classroom__building__in=buildings, day__contains=day).
                         values_list('end_time').distinct().exclude(end_time__isnull=True)
                         .exclude(classroom__building__in=["Unknown", "OFCP"])]

        all_times = start_times + end_times + ['06:00:00', '23:59:00']
        start_end_times = sorted(set(all_times))  # Organizes unique times from earliest to latest
        logger.debug(
            f"calculate_time_blocks - Day: {day}, Building(s): {buildings}, Possible Start/End Times: {start_end_times}")
        time_blocks = []  # Stores the time block tuples for a given day

        if len(start_end_times) > 0:
            # Group the time blocks together if any courses take place on this day
            for i in range(0, len(start_end_times) - 1):
                # Pair every time with the following time to create a series of time blocks
                time_block = [start_end_times[i], start_end_times[i + 1]]
                time_blocks.append(time_block)
            building_time_blocks[day] = time_blocks
            logger.debug(
                f"calculate_time_blocks - List of Time Blocks for {buildings} on {day}: {building_time_blocks}")
    logger.info(f"calculate_time_blocks - Time blocks calculated for {buildings} buildings")
    return building_time_blocks


def calculate_number_classes(buildings='all'):
    """
    Queries the number of classrooms used during each time block and then stores this information in a dictionary.
    Returns an array containing two dictionaries, the first of which containing the time blocks in which a course is
    running inside the specified building and the second containing the recently calculated number of classrooms used
    during each time block.

    :param buildings: specifies which building(s) to return the number of courses for ('all' includes all
    buildings)
    :return           array holding two dictionaries, the first storing time blocks
                      and the second the number of courses running during those time blocks
    """
    time_blocks = calculate_time_blocks(buildings)
    if not time_blocks:
        logger.debug(f"calculate_number_classes - No time blocks found for {buildings}")
        return [{}, {}]
    logger.debug(f"calculate_number_classes - Time blocks found for {buildings}: {time_blocks}")
    all_num_classes = {}  # Dictionary to hold ALL the classroom number data
    for day, day_block_list in time_blocks.items():
        day_num_classes = {}  # Dictionary to hold the classroom number data for a single day
        for block in day_block_list:
            block_start_time = block[0]
            block_end_time = block[1]
            if buildings == 'all':
                # Counts the number of courses (campus-wide) running between the current block's start/end times
                block_num_classes = (Course.objects.all().filter(day__contains=day,
                                                                 start_time__lte=block_start_time,
                                                                 end_time__gte=block_end_time)
                .exclude(classroom__isnull=True).exclude(classroom__building="Unknown").exclude(
                    classroom__building="OFCP"))
            else:
                # Counts the number of courses (within specified buildings) running between the current block's
                # start/end times for a subset of buildings
                block_num_classes = (Course.objects.all().filter(day__contains=day,
                                                                 start_time__lte=block_start_time,
                                                                 end_time__gte=block_end_time,
                                                                 classroom__building__in=buildings)
                .exclude(classroom__isnull=True).exclude(classroom__building="Unknown").exclude(
                    classroom__building="OFCP"))
            logger.debug(f"calculate_number_classes - Buildings: {buildings}, "
                         f"Number of courses held from {block_start_time} - {block_end_time} on {day}: {block_num_classes}")
            # Account for the possibility of several courses in a single classroom by only counting the unique
            # classrooms in use
            unique_classrooms = []
            for course in block_num_classes:
                if course.classroom.name not in unique_classrooms:
                    unique_classrooms.append(course.classroom.name)

            day_num_classes[block_start_time] = len(unique_classrooms)
            logger.debug(f"calculate_number_classes - Number of used classrooms found between "
                         f"{block_start_time} - {block_end_time} on {day}: {unique_classrooms}")
        logger.debug(
            f"calculate_number_classes - Number Classes List for {day} in {buildings} buildings: {day_num_classes}")
        all_num_classes[day] = day_num_classes
    logger.debug(
        f"calculate_number_classes - Number of used classrooms calculated for time blocks in {buildings} buildings: {all_num_classes}")
    logger.info(f"calculate_number_classes - Number of used classrooms calculated for {buildings} buildings")
    return [time_blocks, all_num_classes]


def get_all_buildings():
    """
    Returns a dictionary storing the names of all buildings in the Classroom model.
    """
    buildings_list = Classroom.BUILDINGS
    logger.debug(f"get_all_buildings - Possible Buildings: {buildings_list}")
    return buildings_list


def get_used_classrooms(day: str, start_time: str, end_time: str, buildings: [] = "all") -> {}:
    """
    Returns a list of all classrooms used during a specified time block and data about the course being held in the
    classroom during that specified time block.

    :param day: string specifying which day to search within for used classrooms
    :param start_time: string specifying the start time in which to search for used classrooms
    :param end_time:   string specifying the time in which searching for used classrooms stops
    :param buildings:  string indicating which buildings should be searched for used classrooms
    :return            dictionary containing the data for every classroom being used within the specified time block and
                       building
    """
    # Start/end times must be in HH:MM format
    if not re.match(r'^\d{2}:\d{2}$', start_time) or not re.match(r'^\d{2}:\d{2}$', end_time):
        logger.error(
            f"get_used_classrooms - No classrooms found: Either {start_time} or {end_time} are not in HH:MM format")
        return {}

    if buildings == 'all':
        # Searches for used classrooms within all buildings
        current_courses = (Course.objects.all().filter(day__contains=day,
                                                       start_time__lte=start_time,
                                                       end_time__gte=end_time)
                           .exclude(classroom__isnull=True).exclude(classroom__building__exact="OFCP")).order_by(
            'classroom__building', 'classroom__room_num')
    else:
        # Searches for used classrooms within only buildings specified by the filter
        current_courses = (Course.objects.all().filter(day__contains=day,
                                                       start_time__lte=start_time,
                                                       end_time__gte=end_time,
                                                       classroom__building__in=buildings)
                           .exclude(classroom__isnull=True).exclude(classroom__building__exact="OFCP")).order_by(
            'classroom__building', 'classroom__room_num')
    logger.debug(f"get_used_classrooms - Courses found running between {start_time} and {end_time} on {day} "
                 f"within {buildings} buildings: {current_courses}")
    courses_data = [
        [course.name, course.classroom.name, course.instructor.name, course.classroom.occupancy, course.enrolled]
        for course in current_courses]
    logger.debug(f"get_used_classrooms - Course Data: {courses_data}")

    # Attach the course data to the classroom it is hosted in
    classrooms_dict = {}
    for course_data in courses_data:
        classroom = course_data.pop(1)
        if classroom not in classrooms_dict.keys():
            classrooms_dict[classroom] = [course_data]
        else:
            classrooms_dict[classroom] += [course_data]

    logger.debug(
        f"get_used_classrooms - Classroom data found for {buildings} from {start_time} to {end_time} on {day}: "
        f"{classrooms_dict}")
    logger.info(f"get_used_classrooms - Used Classrooms found from {start_time} to {end_time} on {day}")
    return classrooms_dict


def calculate_classroom_time_blocks(classroom: str):
    """
    Finds all possible time blocks used in the specified classroom and then returns this information in a dictionary.
    This dictionary uses the abbreviation for every weekday ('M', 'T', etc.) as the keys and an array of arrays as
    the values. Each of these value arrays contains many sub-arrays containing the start and end times for the block.
    If no time blocks are found for the specified classroom, an empty dictionary is returned.

    :param  classroom: string representing the name of the classroom to be queried
    :return            dictionary containing every possible time block in which there could be a different course
    """
    days_list = ['M', 'T', 'W', 'th', 'F']
    classroom_time_blocks = {}

    for day in days_list:
        # Finds all start/end times in the specified building on the current day
        start_times = [time[0].strftime("%H:%M:%S") for time in
                       Course.objects.filter(classroom__name=classroom, day__contains=day).values_list('start_time')
                       .distinct().exclude(start_time=None)]
        end_times = [time[0].strftime("%H:%M:%S") for time in
                     Course.objects.filter(classroom__name=classroom, day__contains=day).values_list('end_time')
                     .distinct().exclude(start_time=None)]
        all_times = start_times + end_times + ['06:00:00', '23:59:00']
        start_end_times = sorted(set(all_times))  # Organizes times from earliest to latest
        logger.debug(
            f"calculate_classroom_time_blocks - Start/End Times for courses in {classroom} on {day}: {start_end_times}")
        time_blocks = []  # Stores the time block tuples for a given day

        # Group the time blocks together
        for i in range(0, len(start_end_times) - 1):
            time_block = [start_end_times[i], start_end_times[i + 1]]
            time_blocks.append(time_block)
        classroom_time_blocks[day] = time_blocks
        logger.debug(f"calculate_classroom_time_blocks - Grouped time blocks for {classroom} on {day}: {time_blocks}")

    logger.debug(f"calculate_classroom_time_blocks - List of Time Blocks for {classroom}: {classroom_time_blocks}")
    logger.info(f"calculate_classroom_time_blocks - Time blocks calculated for {classroom}")
    return classroom_time_blocks


def get_classroom_courses(classroom: str) -> {}:
    """
    Finds all courses taking place in the specified classroom. These courses are stored in a dictionary, with all possible
    time periods used as the keys and the name of the course being held during the time block being the value. If there
    are no courses being held in the classroom during a time block, the value for the time block is an empty string.

    :param classroom: string representing the name of the classroom to be queried
    :return           list holding two dictionaries, the first storing time blocks and the second the courses running during
    those time blocks
    """
    time_blocks = calculate_classroom_time_blocks(classroom)
    if not time_blocks:
        logger.debug(f"get_classroom_courses - No time blocks found for {classroom}")
        return [{}, {}]
    classroom_courses = {}  # Dictionary to hold all the courses data
    for day, day_block_list in time_blocks.items():
        day_courses = {}  # Dictionary to hold the classroom's courses during a single day
        for block in day_block_list:
            block_start_time = block[0]
            block_end_time = block[1]
            running_course = Course.objects.all().filter(day__contains=day,
                                                         start_time__lte=block_start_time,
                                                         end_time__gte=block_end_time,
                                                         classroom__name=classroom)
            if len(running_course) == 0:
                courses_data = ["", "", 0]
            else:
                courses_data = [[course.name, course.instructor.name, course.enrolled] for course in running_course]
            day_courses[block_start_time] = courses_data
        logger.debug(f"get_classroom_courses - Courses for {classroom} on {day}: {day_courses}")
        classroom_courses[day] = day_courses

    logger.debug(f"get_classroom_courses - Courses found in {classroom}: {classroom_courses}")
    logger.info(f"get_classroom_courses - Courses found in {classroom}")
    return [time_blocks, classroom_courses]


def get_past_time(day, current_time, buildings='all'):
    """
    Finds the starting time given an ending time for a given day and list of buildings. This is used when paging through
    different times while viewing the used classroom lists.

    :param day:          string specifying which day to look within for time blocks
    :param buildings:    list of buildings to look within for possible time blocks
    :param current_time: string specifying the end time for a block; the paired start time is the desired output
    :return              string detailing the start time associated with the specified end time
    """
    # The day must be M,T,W,th, or F
    if day not in ['M', 'T', 'W', 'th', 'F']:
        logger.error(f"get_past_time - {day} is not a valid day")
        return ''
    # Convert HH:MM format to HH:MM:SS format
    if re.match(r'^\d{2}:\d{2}$', current_time):
        logger.debug(f"Time format of {current_time} changed to HH:MM:SS")
        current_time = f"{current_time}:00"
    # The time must be in HH:MM:SS format for comparison with the times from calculate_time_blocks()
    if not re.match(r'^\d{2}:\d{2}:\d{2}$', current_time):
        logger.error(f"get_past_time - {current_time} is not in HH:MM:SS format")
        return ''
    time_blocks = calculate_time_blocks(buildings)
    for block in time_blocks[day]:
        if block[1] == current_time:
            logger.debug(f"get_past_time - Start Time found: {block[0][:-3]}, Supplied End Time: {current_time}, "
                         f"Day: {day}, Buildings: {buildings}")
            return block[0][:-3]
    # If the time is not found within the time blocks list, return empty string
    logger.debug(f"{current_time} not found on {day} in {buildings} buildings")
    return ''


def get_next_time(day, current_time, buildings='all'):
    """
    Finds the ending time given a start time for a given day and list of buildings. This is used when paging through
    different times while viewing the used classroom lists.

    :param day:          string specifying which day to look within for time blocks
    :param  buildings    list of buildings to look within for possible time blocks
    :param current_time: string specifying the start time which starts the block; the paired end time is the desired output
    :return              string detailing the end time associated with the specified start time
    """
    # The day must be M,T,W,th, or F
    if day not in ['M', 'T', 'W', 'th', 'F']:
        logger.debug(f"get_next_time - {day} is not a valid day")
        return ''
    # Convert HH:MM format to HH:MM:SS format
    if re.match(r'^\d{2}:\d{2}$', current_time):
        logger.debug(f"get_next_time - Time format of {current_time} changed to HH:MM:SS")
        current_time = f"{current_time}:00"
    # The time must be in HH:MM:SS format for comparison with the times from calculate_time_blocks()
    if not re.match(r'^\d{2}:\d{2}:\d{2}$', current_time):
        logger.error(f"get_next_time - {current_time} is not in HH:MM:SS format")
        return ''
    time_blocks = calculate_time_blocks(buildings)
    for block in time_blocks[day]:
        if block[0] == current_time:
            logger.debug(f"get_next_time - End Time found: {block[1][:-3]}, Supplied Start Time: {current_time}, "
                         f"Day: {day}, Buildings: {buildings}")
            return block[1][:-3]
    # If the time is not found within the time blocks list, return empty string
    logger.debug(f"{current_time} not found on {day} in {buildings} buildings")
    return ''


def calculate_day_string(row):
    """
    Creates a string representing the days a class is held on.

    :param row: row of data that represents the course that the day string is calculated for
    """
    days = ""
    if row['CSM_MONDAY'] == 'Y':
        days += 'M'
    if row['CSM_TUESDAY'] == 'Y':
        days += 'T'
    if row['CSM_WEDNESDAY'] == 'Y':
        days += 'W'
    if row['CSM_THURSDAY'] == 'Y':
        days += 'th'
    if row['CSM_FRIDAY'] == 'Y':
        days += 'F'

    logger.debug(f"calculate_day_string - Day String calculated for {row}: {days}")
    return days


def upload_schedule_data(file):
    """
    Creates classroom, instructor, and course objects from the uploaded schedule Excel file and populates the database.
    Any data already present within the database for the term being currently uploaded is replaced.

    :param file: Excel spreadsheet containing the scheduled course data for populating the database
    :return: boolean specifying whether the upload was successful and a list of missing columns. If an invalid file is
             provided or the upload is successful, the missing columns list will be empty.
    """
    missing_columns = []

    # File cannot be empty
    if file is None:
        logger.info("upload_schedule_data - Attempt to upload a schedule without specifying a file")
        return False, missing_columns

    # The file must be an Excel spreadsheet to be uploaded to the DB
    if file.name[-5:] != '.xlsx':
        logger.error(f"upload_schedule_data - Attempt to upload file that was not an .xlsx file: {file.name}")
        return False, missing_columns

    df = pd.read_excel(file)

    # Make sure all the necessary columns are in the uploaded spreadsheet
    necessary_columns = ['SEC_FACULTY_INFO', 'CSM_BLDG', 'CSM_ROOM', 'COURSE_SECTIONS_ID', 'SEC_COURSE_NO', 'SEC_NO',
                         'SEC_TERM', 'SEC_START_DATE', 'SEC_END_DATE', 'SEC_SHORT_TITLE', 'SEC_SUBJECT', 'SEC_MIN_CRED',
                         'SEC_STATUS', 'CSM_START_TIME', 'CSM_END_TIME', 'CSM_INSTR_METHOD',
                         'STUDENTS_AND_RESERVED_SEATS', 'SEC_CAPACITY']

    for column_name in necessary_columns:
        if column_name not in df.columns:
            missing_columns.append(column_name)
    if len(missing_columns) > 0:
        logger.error(
            f"upload_schedule_data - SCHEDULE UPLOAD ABORTED - Schedule spreadsheet upload ({file.name}) was missing columns: {missing_columns}")
        return False, missing_columns

    # Delete all data to prevent different semesters being present in the DB
    Course.objects.all().delete()

    # Create new courses from the uploaded file
    for index, row in df.iterrows():
        instructor, _ = Instructor.objects.get_or_create(
            name=row['SEC_FACULTY_INFO'],
        )
        logger.debug(f"Instructor {instructor} present")

        classroom = None
        # Create a classroom object if it doesn't already exist
        if not pd.isna(row['CSM_BLDG']):
            classroom, created = Classroom.objects.get_or_create(
                name=row['CSM_BLDG'] + "-" + str(row['CSM_ROOM']),
                building=row['CSM_BLDG'],
                room_num=row['CSM_ROOM'],
            )
            if created:
                logger.debug(f"Classroom {classroom} created")

        # Create the course object
        day_string = calculate_day_string(row)
        course = Course.objects.create(
            section_id=None if pd.isna(row['COURSE_SECTIONS_ID']) else row['COURSE_SECTIONS_ID'],
            course_num=None if pd.isna(row['SEC_COURSE_NO']) else row['SEC_COURSE_NO'],
            section_num=None if pd.isna(row['SEC_NO']) else row['SEC_NO'],
            term=None if pd.isna(row['SEC_TERM']) else row['SEC_TERM'],
            start_date=datetime.strptime(row['SEC_START_DATE'], '%b %d %Y').date(),
            end_date=datetime.strptime(row['SEC_END_DATE'], '%b %d %Y').date(),
            name=row['SEC_SHORT_TITLE'],
            subject=row['SEC_SUBJECT'],
            min_credits=None if pd.isna(row['SEC_MIN_CRED']) else row['SEC_MIN_CRED'],
            status=None if pd.isna(row['SEC_STATUS']) else row['SEC_STATUS'],
            start_time=None if pd.isna(row['CSM_START_TIME']) else datetime.strptime(row['CSM_START_TIME'],
                                                                                     '%I:%M%p').time(),
            end_time=None if pd.isna(row['CSM_END_TIME']) else datetime.strptime(row['CSM_END_TIME'],
                                                                                 '%I:%M%p').time(),
            day=day_string,
            classroom=classroom if classroom is not None else None,
            instruction_method=row['CSM_INSTR_METHOD'],
            instructor=instructor,
            enrolled=None if pd.isna(row['STUDENTS_AND_RESERVED_SEATS']) else row['STUDENTS_AND_RESERVED_SEATS'],
            capacity=None if pd.isna(row['SEC_CAPACITY']) else row['SEC_CAPACITY'],
        )
        logger.debug(f"Course {course} created")

    logger.info(f"New Course Schedule Spreadsheet Uploaded: {file.name}")
    return True, None


def upload_classroom_data(file):
    """
    Creates new classroom objects using Dan Case's classroom data and populates the database. Any classrooms mentioned
    in uploaded Excel spreadsheet replace the classroom data currently in the database.

    :param file: Excel spreadsheet containing the classroom specification data for populating the database
    :return: True if the specified file was successfully uploaded into the DB; False if the file was not a .xlsx file,
             or if there were necessary columns missing from the spreadsheet
    """
    missing_columns = []

    # File cannot be empty
    if file is None:
        logger.info("upload_classroom_data - Attempt to upload a schedule without specifying a file")
        return False, missing_columns

    # The file must be an Excel spreadsheet
    if file.name[-5:] != '.xlsx':
        logger.error(f"upload_classroom_data - Attempt to upload file that was not an .xlsx file: {file.name}")
        return False, missing_columns

    df = pd.read_excel(file)

    # Make sure all the necessary columns are in the uploaded spreadsheet
    necessary_columns = ['Building Information', 'Room Number', 'Number of Student Seats in Room', 'Width of Room',
                         'Length of Room', 'Number of Projectors in Room', 'Does room have any of the following?',
                         'Any other things of note in Room (TV or Periodic Table poster)', 'Notes']

    for column_name in necessary_columns:
        if column_name not in df.columns:
            missing_columns.append(column_name)
    if len(missing_columns) > 0:
        logger.error(
            f"CLASSROOM UPLOAD ABORTED - Classroom spreadsheet upload ({file.name}) was missing columns: {missing_columns}")
        return False, missing_columns

    for index, row in df.iterrows():
        features = ""
        features += row['Does room have any of the following?'] \
            if not pd.isna(row['Does room have any of the following?']) else ""
        features += row['Any other things of note in Room (TV or Periodic Table poster)'] \
            if not pd.isna(row['Any other things of note in Room (TV or Periodic Table poster)']) else ""
        logger.debug(f"upload_classroom_data: Classroom Features: {features}")

        # Create the new updated classroom object
        classroom, _ = Classroom.objects.update_or_create(
            name=row['Building Information'] + "-" + str(row['Room Number']),
            defaults={
                'building': row['Building Information'].strip(),
                'room_num': row['Room Number'],
                'occupancy': row['Number of Student Seats in Room'] if not pd.isna(
                    row['Number of Student Seats in Room']) else None,
                'width': row['Width of Room'] if not pd.isna(row['Width of Room']) else None,
                'length': row['Length of Room'] if not pd.isna(row['Length of Room']) else None,
                'projector_num': row['Number of Projectors in Room'] if not pd.isna(
                    row['Number of Projectors in Room']) else None,
                'features': features,
                'notes': row['Notes'] if not pd.isna(row['Notes']) else None,
            }
        )
        logger.debug(f"Classroom {classroom} created/updated")

    logger.info(f"Classroom spreadsheet uploaded successfully: {file.name}")
    return True, missing_columns
