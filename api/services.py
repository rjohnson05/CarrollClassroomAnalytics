from datetime import datetime

from api.models import Course, Classroom, Instructor
import logging
import pandas as pd

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
            # Finds all start/end times on the current day from ALL buildings and converts them from datetime objects to strings
            start_times = [time[0].strftime("%H:%M:%S") for time in
                           Course.objects.filter(day__contains=day).values_list(
                               'start_time').distinct().exclude(start_time__isnull=True).exclude(
                               classroom__building="Unknown")]
            end_times = [time[0].strftime("%H:%M:%S") for time in
                         Course.objects.values_list('end_time').filter(day__contains=day).distinct()
                         .exclude(end_time__isnull=True).exclude(classroom__building="Unknown")]
        else:
            # Finds all start/end times in the specified building on the current day
            start_times = [time[0].strftime("%H:%M:%S") for time in
                           Course.objects.filter(classroom__building__in=buildings, day__contains=day).values_list(
                               'start_time').distinct().exclude(start_time__isnull=True)]
            end_times = [time[0].strftime("%H:%M:%S") for time in
                         Course.objects.values_list('end_time').filter(classroom__building__in=buildings,
                                                                       day__contains=day).distinct().exclude(
                             end_time__isnull=True)]
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
                block_num_classes = (Course.objects.all().filter(day__contains=day,
                                                                 start_time__lte=block_start_time,
                                                                 end_time__gte=block_end_time)
                                     .exclude(classroom__isnull=True).exclude(classroom__building="Unknown").exclude(classroom__building="OFCP"))
            else:
                # Counts the number of courses (within specified buildings) running between the current block's
                # start/end times for a subset of buildings
                block_num_classes = (Course.objects.all().filter(day__contains=day,
                                                                 start_time__lte=block_start_time,
                                                                 end_time__gte=block_end_time,
                                                                 classroom__building__in=buildings)
                                     .exclude(classroom__isnull=True).exclude(classroom__building="Unknown").exclude(classroom__building="OFCP"))
            # Account for the possibility of several courses in a single classrooms by only counting the unique
            # classrooms in use
            unique_classrooms = []
            for course in block_num_classes:
                if course.classroom.name not in unique_classrooms:
                    unique_classrooms.append(course.classroom.name)

            day_num_classes[block_start_time] = len(unique_classrooms)
            logger.debug(f"calculate_number_classes: Unique classes found for block {block_start_time} on {day}: {unique_classrooms}")
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


def get_used_classrooms(day: str, start_time: str, end_time: str, buildings: str = "all") -> {}:
    """
    Returns a list of all classrooms used during a specified time block and data about the course being held in the
    classroom during the specified time block.

    :param day: String specifying which day to search within for used classrooms
    :param start_time: String specifying the start time in which to search for used classrooms
    :param end_time: String specifying the time in which searching for used classrooms stops
    :param buildings: String indicating which buildings should be searched for used classrooms
    :return Dictionary containing the data for every classroom being used within the specified time block and building
    """
    if buildings == 'all':
        current_courses = (Course.objects.all().filter(day__contains=day,
                                                       start_time__lte=start_time,
                                                       end_time__gte=end_time)
                           .exclude(classroom__isnull=True).exclude(classroom__building__exact="OFCP"))
    else:
        current_courses = (Course.objects.all().filter(day__contains=day,
                                                       start_time__lte=start_time,
                                                       end_time__gte=end_time,
                                                       classroom__building__in=buildings)
                           .exclude(classroom__isnull=True).exclude(classroom__building__exact="OFCP"))
    courses_data = [
        [course.name, course.classroom.name, course.instructor, course.classroom.occupancy, course.enrolled]
        for course in current_courses]

    classrooms_dict = {}
    for course_data in courses_data:
        classroom = course_data.pop(1)
        if classroom not in classrooms_dict.keys():
            classrooms_dict[classroom] = [course_data]
        else:
            classrooms_dict[classroom] += [course_data]

    logger.debug(f"get_used_classrooms: Classroom data found for {buildings} from {start_time} to {end_time} on {day}: {classrooms_dict}")
    return classrooms_dict


def calculate_classroom_time_blocks(classroom: str) -> []:
    """
    Finds all possible time blocks used in the specified classroom and then returns this information in a dictionary.
    This dictionary uses the abbreviation for every weekday ('M', 'T', etc.) as the keys and an array of arrays as
    the values. Each of these value arrays contains many sub-arrays containing the start and end times for the block.
    If no time blocks are found for the specified classroom, an empty dictionary is returned.

    :param  classroom        String representing the name of the classroom to be queried
    :return  Dictionary containing every possible time block in which there could be a different course
    """
    logger.debug(f"services.calculate_classroom_time_blocks: Classroom Name: {classroom}")
    days_list = ['M', 'T', 'W', 'th', 'F']
    classroom_time_blocks = {}
    for day in days_list:
        # Finds all start/end times in the specified building on the current day
        start_times = [time[0].strftime("%H:%M:%S") for time in
                       Course.objects.filter(classroom__name=classroom, day__contains=day).values_list(
                           'start_time').distinct()]
        end_times = [time[0].strftime("%H:%M:%S") for time in
                     Course.objects.values_list('end_time').filter(classroom__name=classroom,
                                                                   day__contains=day).distinct()]
        all_times = start_times + end_times + ['06:00:00', '23:59:00']
        start_end_times = sorted(set(all_times))  # Organizes times from earliest to latest
        logger.debug(f"calculate_classroom_time_blocks: Possible Start/End Times: {start_end_times}")
        time_blocks = []  # Stores the time block tuples for a given day

        if len(start_end_times) > 0:
            # Group the time blocks together
            for i in range(0, len(start_end_times) - 1):
                time_block = [start_end_times[i], start_end_times[i + 1]]
                time_blocks.append(time_block)
            classroom_time_blocks[day] = time_blocks
            logger.debug(f"List of Time Blocks for {classroom}: {classroom_time_blocks}")
    return classroom_time_blocks


def get_classroom_courses(classroom: str) -> {}:
    """
    Finds all courses taking place in the specified classroom. These courses are stored in a dictionary, with all possible
    time periods used as the keys and the name of the course being held during the time block being the value. If there
    are no courses being held in the classroom during a time block, the value for the time block is an empty string.

    :param classroom: String representing the name of the classroom to be queried
    :returns: List holding two dictionaries, the first storing time blocks and the second the courses running during
    those time blocks
    """
    time_blocks = calculate_classroom_time_blocks(classroom)
    if not time_blocks:
        logger.debug(f"get_classroom_courses: No time blocks found for {classroom}")
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
            courses_data = [[course.name, course.instructor, course.enrolled] for course in running_course]
            if len(running_course) == 0:
                courses_data = ["", "", 0]
            day_courses[block_start_time] = courses_data
        logger.debug(f"get_classroom_courses: Courses for {classroom} on {day}: {day_courses}")
        classroom_courses[day] = day_courses
    logger.debug(f"get_classroom_courses: Courses found in {classroom}: {classroom_courses}")
    return [time_blocks, classroom_courses]


def calculate_day_string(row):
    """
    Creates a string representing the days a class is held on.

    :param row: Row of data that represents the course that the day string is calculated for
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

    logger.debug(f"calculate_day_string: Day String calculated for {row}: {days}")
    return days


def upload_schedule_data(file):
    """
    Creates classroom, instructor, and course objects from the uploaded schedule Excel file and populates the database.
    Any data already present within the database for the term being currently uploaded is replaced.

    :param file: Excel spreadsheet containing the scheduled course data for populating the database
    """
    logger.info("New schedule file uploading")
    df = pd.read_excel(file)

    # Delete all courses already in the database for the term being modified
    current_term = df['SEC_TERM'][0]
    current_term_courses = Course.objects.all().filter(term__exact=current_term)
    current_term_courses.delete()

    # Create new courses from the uploaded file
    for index, row in df.iterrows():
        instructor, _ = Instructor.objects.get_or_create(
            name=row['SEC_FACULTY_INFO'],
        )
        logger.debug(f"Instructor {instructor} present")

        classroom = None
        if not pd.isna(row['CSM_BLDG']):
            classroom, _ = Classroom.objects.get_or_create(
                name=row['CSM_BLDG'] + "-" + str(row['CSM_ROOM']),
                building=row['CSM_BLDG'],
                room_num=row['CSM_ROOM'],
            )
            logger.debug(f"Classroom {classroom} present")

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
            end_time=None if pd.isna(row['CSM_START_TIME']) else datetime.strptime(row['CSM_END_TIME'],
                                                                                   '%I:%M%p').time(),
            day=day_string,
            classroom=classroom if classroom is not None else None,
            instruction_method=row['CSM_INSTR_METHOD'],
            instructor=instructor,
            enrolled=None if pd.isna(row['STUDENTS_AND_RESERVED_SEATS']) else row['STUDENTS_AND_RESERVED_SEATS'],
            capacity=None if pd.isna(row['SEC_CAPACITY']) else row['SEC_CAPACITY'],
        )
        logger.debug(f"Course {course} created")


def upload_classroom_data(file):
    """
    Creates new classroom objects using Dan Case's classroom data and populates the database. Any classrooms mentioned
    in uploaded Excel spreadsheet replace the classroom data currently in the database.

    :param file: Excel spreadsheet containing the classroom specification data for populating the database
    """
    logger.info("New classroom data uploading")
    df = pd.read_excel(file)

    correct_bldg_names_dict = {
        "SH": "SIMP",
        "OC": "OCON",
        "STCH": "STCH",
        "CUBE": "CUBE",
        "ENG": "CENG",
        "ANZ": "PCCC",
        "PE": "PECT",
        "GUAD": "GUAD"
    }

    for index, row in df.iterrows():
        features = ""
        features += row['Does room have any of the following?'] \
            if not pd.isna(row['Does room have any of the following?']) else ""
        features += row['Any other things of note in Room (TV or Periodic Table poster)'] \
            if not pd.isna(row['Any other things of note in Room (TV or Periodic Table poster)']) else ""
        logger.debug(f"upload_classroom_data: Classroom Features: {features}")

        # Create the new updated classroom object
        classroom = Classroom.objects.update_or_create(
            name=correct_bldg_names_dict[row['Building Information']] + "-" + str(row['Room Number']),
            building=correct_bldg_names_dict[row['Building Information']],
            room_num=row['Room Number'],
            occupancy=row['Number of Student Seats in Room'] if not pd.isna(
                row['Number of Student Seats in Room']) else None,
            width=row['Width of Room'] if not pd.isna(row['Width of Room']) else None,
            length=row['Length of Room'] if not pd.isna(row['Length of Room']) else None,
            projector_num=row['Number of Projectors in Room'] if not pd.isna(
                row['Number of Projectors in Room']) else None,
            features=features,
            notes=row['Notes'] if not pd.isna(row['Notes']) else None,
        )
        logger.debug(f"Classroom {classroom} created/updated")