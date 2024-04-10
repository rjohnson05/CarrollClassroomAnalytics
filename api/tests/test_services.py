import datetime

from django.test import TestCase

from api import services
from api.models import Instructor, Classroom, Course


class CalculateTimeBlocks(TestCase):
    # Creates a MWF course in SIMP at the designated start/end time
    @classmethod
    def create_simp_mwf_course(cls, start_time=None, end_time=None):
        classroom = Classroom.objects.get(name="SIMP-120")
        instructor = Instructor.objects.get(name="Nathan Williams")

        Course.objects.create(
            section_id=1,
            course_num="123",
            section_num="A",
            term="2024SPR",
            start_date=datetime.date(2024, 4, 4),
            end_date=datetime.date(2024, 4, 5),
            name="Advanced Software Engineering",
            subject="CS",
            status="A",
            day="MWF",
            classroom=classroom,
            instruction_method="LEC",
            instructor=instructor,
            start_time=start_time,
            end_time=end_time
        )

    # Creates a Tth course in SIMP at the designated start/end time
    @classmethod
    def create_simp_tth_course(cls, start_time=None, end_time=None):
        classroom = Classroom.objects.get(name="SIMP-120")
        instructor = Instructor.objects.get(name="Nathan Williams")

        Course.objects.create(
            section_id=1,
            course_num="123",
            section_num="A",
            term="2024SPR",
            start_date=datetime.date(2024, 4, 4),
            end_date=datetime.date(2024, 4, 5),
            name="Advanced Software Engineering",
            subject="CS",
            status="A",
            day="Tth",
            classroom=classroom,
            instruction_method="LEC",
            instructor=instructor,
            start_time=start_time,
            end_time=end_time
        )

    # Creates a MWF course in STCH at the designated start/end time
    @classmethod
    def create_STCH_course(cls, start_time=None, end_time=None):
        classroom = Classroom.objects.get(name="STCH-120")
        instructor = Instructor.objects.get(name="Brent Northup")

        Course.objects.create(
            section_id=1,
            course_num="123",
            section_num="A",
            term="2024SPR",
            start_date=datetime.date(2024, 4, 4),
            end_date=datetime.date(2024, 4, 5),
            name="Small Group Communication",
            subject="CS",
            status="A",
            day="MWF",
            classroom=classroom,
            instruction_method="LEC",
            instructor=instructor,
            start_time=start_time,
            end_time=end_time
        )

    # Sets up the classrooms and instructors necessary for adding courses within each test
    def setUp(self):
        Instructor.objects.create(
            name="Nathan Williams"
        )
        Instructor.objects.create(
            name="Brent Northup"
        )
        Classroom.objects.create(
            name="SIMP-120",
            building="SIMP",
            room_num="120"
        )
        Classroom.objects.create(
            name="STCH-120",
            building="STCH",
            room_num="120"
        )

    # Ensures that only the first and last times of the day are returned in time blocks where there are no courses
    # present
    def test_time_blocks_no_courses(self):
        time_blocks = services.calculate_time_blocks("all")
        predicted_time_blocks = {'M': [['06:00:00', '23:59:00']],
                                 'T': [['06:00:00', '23:59:00']],
                                 'W': [['06:00:00', '23:59:00']],
                                 'th': [['06:00:00', '23:59:00']],
                                 'F': [['06:00:00', '23:59:00']]}
        self.assertEqual(time_blocks, predicted_time_blocks)

    # Ensures that only the first and last times of the day are returned in time blocks when there are courses present,
    # but none with time data
    def test_no_time_blocks_with_course(self):
        self.create_simp_mwf_course()
        time_blocks = services.calculate_time_blocks("all")
        predicted_time_blocks = {'M': [['06:00:00', '23:59:00']],
                                 'T': [['06:00:00', '23:59:00']],
                                 'W': [['06:00:00', '23:59:00']],
                                 'th': [['06:00:00', '23:59:00']],
                                 'F': [['06:00:00', '23:59:00']]}
        self.assertEqual(time_blocks, predicted_time_blocks)

    # Ensures that the proper time blocks are returned when one classroom with start/end times is present on MWF
    def test_mwf_time_blocks_with_single_course(self):
        self.create_simp_mwf_course(datetime.time(hour=8, minute=00), datetime.time(hour=8, minute=50))
        time_blocks = services.calculate_time_blocks("all")
        predicted_time_blocks = {'M': [['06:00:00', '08:00:00'], ['08:00:00', '08:50:00'], ['08:50:00', '23:59:00']],
                                 'T': [['06:00:00', '23:59:00']],
                                 'W': [['06:00:00', '08:00:00'], ['08:00:00', '08:50:00'], ['08:50:00', '23:59:00']],
                                 'th': [['06:00:00', '23:59:00']],
                                 'F': [['06:00:00', '08:00:00'], ['08:00:00', '08:50:00'], ['08:50:00', '23:59:00']]}
        self.assertEqual(time_blocks, predicted_time_blocks)

    # Ensures that the proper time blocks are returned when two classrooms with different start/end times are present
    # on MWF
    def test_mwf_time_blocks_with_multiple_different_courses(self):
        self.create_simp_mwf_course(datetime.time(hour=8, minute=00), datetime.time(hour=8, minute=50))
        self.create_simp_mwf_course(datetime.time(hour=9, minute=00), datetime.time(hour=9, minute=50))
        time_blocks = services.calculate_time_blocks("all")
        predicted_time_blocks = {'M': [['06:00:00', '08:00:00'], ['08:00:00', '08:50:00'], ['08:50:00', '09:00:00'],
                                       ['09:00:00', '09:50:00'], ['09:50:00', '23:59:00']],
                                 'T': [['06:00:00', '23:59:00']],
                                 'W': [['06:00:00', '08:00:00'], ['08:00:00', '08:50:00'], ['08:50:00', '09:00:00'],
                                       ['09:00:00', '09:50:00'], ['09:50:00', '23:59:00']],
                                 'th': [['06:00:00', '23:59:00']],
                                 'F': [['06:00:00', '08:00:00'], ['08:00:00', '08:50:00'], ['08:50:00', '09:00:00'],
                                       ['09:00:00', '09:50:00'], ['09:50:00', '23:59:00']]}
        self.assertEqual(time_blocks, predicted_time_blocks)

    # Ensures that the proper time blocks are returned when two classrooms with the same start/end times are present
    # on MWF
    def test_mwf_time_blocks_with_multiple_same_courses(self):
        self.create_simp_mwf_course(datetime.time(hour=8, minute=00), datetime.time(hour=8, minute=50))
        self.create_simp_mwf_course(datetime.time(hour=8, minute=00), datetime.time(hour=8, minute=50))
        time_blocks = services.calculate_time_blocks("all")
        predicted_time_blocks = {'M': [['06:00:00', '08:00:00'], ['08:00:00', '08:50:00'], ['08:50:00', '23:59:00']],
                                 'T': [['06:00:00', '23:59:00']],
                                 'W': [['06:00:00', '08:00:00'], ['08:00:00', '08:50:00'], ['08:50:00', '23:59:00']],
                                 'th': [['06:00:00', '23:59:00']],
                                 'F': [['06:00:00', '08:00:00'], ['08:00:00', '08:50:00'], ['08:50:00', '23:59:00']]}
        self.assertEqual(time_blocks, predicted_time_blocks)

    # Ensures that the proper time blocks are returned when one course with start/end times is present on Tth
    def test_tth_time_blocks_with_single_course(self):
        self.create_simp_tth_course(datetime.time(hour=8, minute=00), datetime.time(hour=9, minute=15))
        time_blocks = services.calculate_time_blocks("all")
        predicted_time_blocks = {
            'M': [['06:00:00', '23:59:00']],
            'T': [['06:00:00', '08:00:00'], ['08:00:00', '09:15:00'], ['09:15:00', '23:59:00']],
            'W': [['06:00:00', '23:59:00']],
            'th': [['06:00:00', '08:00:00'], ['08:00:00', '09:15:00'], ['09:15:00', '23:59:00']],
            'F': [['06:00:00', '23:59:00']]}
        self.assertEqual(time_blocks, predicted_time_blocks)

    # Ensures that the proper time blocks are returned when two classrooms with different start/end times are present
    # on Tth
    def test_tth_time_blocks_with_multiple_different_courses(self):
        self.create_simp_tth_course(datetime.time(hour=8, minute=00), datetime.time(hour=9, minute=15))
        self.create_simp_tth_course(datetime.time(hour=9, minute=30), datetime.time(hour=10, minute=45))
        time_blocks = services.calculate_time_blocks("all")
        predicted_time_blocks = {'M': [['06:00:00', '23:59:00']],
                                 'T': [['06:00:00', '08:00:00'], ['08:00:00', '09:15:00'], ['09:15:00', '09:30:00'],
                                       ['09:30:00', '10:45:00'], ['10:45:00', '23:59:00']],
                                 'W': [['06:00:00', '23:59:00']],
                                 'th': [['06:00:00', '08:00:00'], ['08:00:00', '09:15:00'], ['09:15:00', '09:30:00'],
                                        ['09:30:00', '10:45:00'], ['10:45:00', '23:59:00']],
                                 'F': [['06:00:00', '23:59:00']]}
        self.assertEqual(time_blocks, predicted_time_blocks)

    # Ensures that the proper time blocks are returned when two classrooms with the same start/end times are present
    # on Tth
    def test_tth_time_blocks_with_multiple_same_courses(self):
        self.create_simp_tth_course(datetime.time(hour=8, minute=00), datetime.time(hour=9, minute=15))
        self.create_simp_tth_course(datetime.time(hour=8, minute=00), datetime.time(hour=9, minute=15))
        time_blocks = services.calculate_time_blocks("all")
        predicted_time_blocks = {
            'M': [['06:00:00', '23:59:00']],
            'T': [['06:00:00', '08:00:00'], ['08:00:00', '09:15:00'], ['09:15:00', '23:59:00']],
            'W': [['06:00:00', '23:59:00']],
            'th': [['06:00:00', '08:00:00'], ['08:00:00', '09:15:00'], ['09:15:00', '23:59:00']],
            'F': [['06:00:00', '23:59:00']]}
        self.assertEqual(time_blocks, predicted_time_blocks)

    # Ensures that only the first and last times of the day are returned in time blocks where there are no courses
    # present, but now specifying to look in a single building
    def test_time_blocks_no_courses_one_building(self):
        time_blocks = services.calculate_time_blocks(["SIMP"])
        predicted_time_blocks = {'M': [['06:00:00', '23:59:00']],
                                 'T': [['06:00:00', '23:59:00']],
                                 'W': [['06:00:00', '23:59:00']],
                                 'th': [['06:00:00', '23:59:00']],
                                 'F': [['06:00:00', '23:59:00']]}
        self.assertEqual(time_blocks, predicted_time_blocks)

    # Ensures that only the first and last times of the day are returned in time blocks when there are courses present,
    # but none with time data, but now specifying to look in a single building
    def test_no_time_blocks_with_course_one_building(self):
        self.create_simp_mwf_course()
        time_blocks = services.calculate_time_blocks(["SIMP"])
        predicted_time_blocks = {'M': [['06:00:00', '23:59:00']],
                                 'T': [['06:00:00', '23:59:00']],
                                 'W': [['06:00:00', '23:59:00']],
                                 'th': [['06:00:00', '23:59:00']],
                                 'F': [['06:00:00', '23:59:00']]}
        self.assertEqual(time_blocks, predicted_time_blocks)

    # Ensures that the proper time blocks are returned when one classroom with start/end times is present on MWF,
    # but now specifying to look in a single building
    def test_mwf_time_blocks_with_single_course_one_building(self):
        self.create_simp_mwf_course(datetime.time(hour=8, minute=00), datetime.time(hour=8, minute=50))
        time_blocks = services.calculate_time_blocks(["SIMP"])
        predicted_time_blocks = {
            'M': [['06:00:00', '08:00:00'], ['08:00:00', '08:50:00'], ['08:50:00', '23:59:00']],
            'T': [['06:00:00', '23:59:00']],
            'W': [['06:00:00', '08:00:00'], ['08:00:00', '08:50:00'], ['08:50:00', '23:59:00']],
            'th': [['06:00:00', '23:59:00']],
            'F': [['06:00:00', '08:00:00'], ['08:00:00', '08:50:00'], ['08:50:00', '23:59:00']]}
        self.assertEqual(time_blocks, predicted_time_blocks)

    # Ensures that the proper time blocks are returned when two classrooms with different start/end times are present
    # on MWF, but now specifying to look in a single building
    def test_mwf_time_blocks_with_multiple_different_courses_one_building(self):
        self.create_simp_mwf_course(datetime.time(hour=8, minute=00), datetime.time(hour=8, minute=50))
        self.create_simp_mwf_course(datetime.time(hour=9, minute=00), datetime.time(hour=9, minute=50))
        time_blocks = services.calculate_time_blocks(["SIMP"])
        predicted_time_blocks = {'M': [['06:00:00', '08:00:00'], ['08:00:00', '08:50:00'], ['08:50:00', '09:00:00'],
                                       ['09:00:00', '09:50:00'], ['09:50:00', '23:59:00']],
                                 'T': [['06:00:00', '23:59:00']],
                                 'W': [['06:00:00', '08:00:00'], ['08:00:00', '08:50:00'], ['08:50:00', '09:00:00'],
                                       ['09:00:00', '09:50:00'], ['09:50:00', '23:59:00']],
                                 'th': [['06:00:00', '23:59:00']],
                                 'F': [['06:00:00', '08:00:00'], ['08:00:00', '08:50:00'], ['08:50:00', '09:00:00'],
                                       ['09:00:00', '09:50:00'], ['09:50:00', '23:59:00']]}
        self.assertEqual(time_blocks, predicted_time_blocks)

    # Ensures that the proper time blocks are returned when two classrooms with the same start/end times are present
    # on MWF, but now specifying to look in a single building
    def test_mwf_time_blocks_with_multiple_same_courses_one_building(self):
        self.create_simp_mwf_course(datetime.time(hour=8, minute=00), datetime.time(hour=8, minute=50))
        self.create_simp_mwf_course(datetime.time(hour=8, minute=00), datetime.time(hour=8, minute=50))
        time_blocks = services.calculate_time_blocks(["SIMP"])
        predicted_time_blocks = {
            'M': [['06:00:00', '08:00:00'], ['08:00:00', '08:50:00'], ['08:50:00', '23:59:00']],
            'T': [['06:00:00', '23:59:00']],
            'W': [['06:00:00', '08:00:00'], ['08:00:00', '08:50:00'], ['08:50:00', '23:59:00']],
            'th': [['06:00:00', '23:59:00']],
            'F': [['06:00:00', '08:00:00'], ['08:00:00', '08:50:00'], ['08:50:00', '23:59:00']]}
        self.assertEqual(time_blocks, predicted_time_blocks)

    # Ensures that the proper time blocks are returned when one course with start/end times is present on Tth,
    # but now specifying to look in a single building
    def test_tth_time_blocks_with_single_course_one_building(self):
        self.create_simp_tth_course(datetime.time(hour=8, minute=00), datetime.time(hour=9, minute=15))
        time_blocks = services.calculate_time_blocks(["SIMP"])
        predicted_time_blocks = {
            'M': [['06:00:00', '23:59:00']],
            'T': [['06:00:00', '08:00:00'], ['08:00:00', '09:15:00'], ['09:15:00', '23:59:00']],
            'W': [['06:00:00', '23:59:00']],
            'th': [['06:00:00', '08:00:00'], ['08:00:00', '09:15:00'], ['09:15:00', '23:59:00']],
            'F': [['06:00:00', '23:59:00']]}
        self.assertEqual(time_blocks, predicted_time_blocks)

    # Ensures that the proper time blocks are returned when two classrooms with different start/end times are present
    # on Tth, but now specifying to look in a single building
    def test_tth_time_blocks_with_multiple_different_courses_one_building(self):
        self.create_simp_tth_course(datetime.time(hour=8, minute=00), datetime.time(hour=9, minute=15))
        self.create_simp_tth_course(datetime.time(hour=9, minute=30), datetime.time(hour=10, minute=45))
        time_blocks = services.calculate_time_blocks(["SIMP"])
        predicted_time_blocks = {'M': [['06:00:00', '23:59:00']],
                                 'T': [['06:00:00', '08:00:00'], ['08:00:00', '09:15:00'], ['09:15:00', '09:30:00'],
                                       ['09:30:00', '10:45:00'], ['10:45:00', '23:59:00']],
                                 'W': [['06:00:00', '23:59:00']],
                                 'th': [['06:00:00', '08:00:00'], ['08:00:00', '09:15:00'],
                                        ['09:15:00', '09:30:00'], ['09:30:00', '10:45:00'],
                                        ['10:45:00', '23:59:00']],
                                 'F': [['06:00:00', '23:59:00']]}
        self.assertEqual(time_blocks, predicted_time_blocks)

    # Ensures that the proper time blocks are returned when two classrooms with the same start/end times are present
    # on Tth, but now specifying to look in a single building
    def test_tth_time_blocks_with_multiple_same_courses_one_building(self):
        self.create_simp_tth_course(datetime.time(hour=8, minute=00), datetime.time(hour=9, minute=15))
        self.create_simp_tth_course(datetime.time(hour=8, minute=00), datetime.time(hour=9, minute=15))
        time_blocks = services.calculate_time_blocks(["SIMP"])
        predicted_time_blocks = {
            'M': [['06:00:00', '23:59:00']],
            'T': [['06:00:00', '08:00:00'], ['08:00:00', '09:15:00'], ['09:15:00', '23:59:00']],
            'W': [['06:00:00', '23:59:00']],
            'th': [['06:00:00', '08:00:00'], ['08:00:00', '09:15:00'], ['09:15:00', '23:59:00']],
            'F': [['06:00:00', '23:59:00']]}
        self.assertEqual(time_blocks, predicted_time_blocks)

    # Ensures that only the first and last times of the day are returned in time blocks where there are no courses
    # present, but now specifying to look in several buildings
    def test_time_blocks_no_courses_multiple_buildings(self):
        time_blocks = services.calculate_time_blocks(["SIMP", "STCH"])
        predicted_time_blocks = {'M': [['06:00:00', '23:59:00']],
                                 'T': [['06:00:00', '23:59:00']],
                                 'W': [['06:00:00', '23:59:00']],
                                 'th': [['06:00:00', '23:59:00']],
                                 'F': [['06:00:00', '23:59:00']]}
        self.assertEqual(time_blocks, predicted_time_blocks)

    # Ensures that only the first and last times of the day are returned in time blocks when there are courses present,
    # but none with time data, but now specifying to look in several buildings
    def test_no_time_blocks_with_course_multiple_buildings(self):
        self.create_simp_mwf_course()
        time_blocks = services.calculate_time_blocks(["SIMP", "STCH"])
        predicted_time_blocks = {'M': [['06:00:00', '23:59:00']],
                                 'T': [['06:00:00', '23:59:00']],
                                 'W': [['06:00:00', '23:59:00']],
                                 'th': [['06:00:00', '23:59:00']],
                                 'F': [['06:00:00', '23:59:00']]}
        self.assertEqual(time_blocks, predicted_time_blocks)

    # Ensures that the proper time blocks are returned when one classroom with start/end times is present on MWF,
    # but now specifying to look in several buildings
    def test_mwf_time_blocks_with_single_course_multiple_buildings(self):
        self.create_simp_mwf_course(datetime.time(hour=8, minute=00), datetime.time(hour=8, minute=50))
        time_blocks = services.calculate_time_blocks(["SIMP", "STCH"])
        predicted_time_blocks = {
            'M': [['06:00:00', '08:00:00'], ['08:00:00', '08:50:00'], ['08:50:00', '23:59:00']],
            'T': [['06:00:00', '23:59:00']],
            'W': [['06:00:00', '08:00:00'], ['08:00:00', '08:50:00'], ['08:50:00', '23:59:00']],
            'th': [['06:00:00', '23:59:00']],
            'F': [['06:00:00', '08:00:00'], ['08:00:00', '08:50:00'], ['08:50:00', '23:59:00']]}
        self.assertEqual(time_blocks, predicted_time_blocks)

    # Ensures that the proper time blocks are returned when two classrooms with different start/end times are present
    # on MWF, but now specifying to look in several buildings
    def test_mwf_time_blocks_with_multiple_different_courses_multiple_buildings(self):
        self.create_simp_mwf_course(datetime.time(hour=8, minute=00), datetime.time(hour=8, minute=50))
        self.create_simp_mwf_course(datetime.time(hour=9, minute=00), datetime.time(hour=9, minute=50))
        time_blocks = services.calculate_time_blocks(["SIMP", "STCH"])
        predicted_time_blocks = {'M': [['06:00:00', '08:00:00'], ['08:00:00', '08:50:00'], ['08:50:00', '09:00:00'],
                                       ['09:00:00', '09:50:00'], ['09:50:00', '23:59:00']],
                                 'T': [['06:00:00', '23:59:00']],
                                 'W': [['06:00:00', '08:00:00'], ['08:00:00', '08:50:00'], ['08:50:00', '09:00:00'],
                                       ['09:00:00', '09:50:00'], ['09:50:00', '23:59:00']],
                                 'th': [['06:00:00', '23:59:00']],
                                 'F': [['06:00:00', '08:00:00'], ['08:00:00', '08:50:00'], ['08:50:00', '09:00:00'],
                                       ['09:00:00', '09:50:00'], ['09:50:00', '23:59:00']]}
        self.assertEqual(time_blocks, predicted_time_blocks)

    # Ensures that the proper time blocks are returned when two classrooms with the same start/end times are present
    # on MWF, but now specifying to look in several buildings
    def test_mwf_time_blocks_with_multiple_same_courses_multiple_buildings(self):
        self.create_simp_mwf_course(datetime.time(hour=8, minute=00), datetime.time(hour=8, minute=50))
        self.create_simp_mwf_course(datetime.time(hour=8, minute=00), datetime.time(hour=8, minute=50))
        time_blocks = services.calculate_time_blocks(["SIMP", "STCH"])
        predicted_time_blocks = {
            'M': [['06:00:00', '08:00:00'], ['08:00:00', '08:50:00'], ['08:50:00', '23:59:00']],
            'T': [['06:00:00', '23:59:00']],
            'W': [['06:00:00', '08:00:00'], ['08:00:00', '08:50:00'], ['08:50:00', '23:59:00']],
            'th': [['06:00:00', '23:59:00']],
            'F': [['06:00:00', '08:00:00'], ['08:00:00', '08:50:00'], ['08:50:00', '23:59:00']]}
        self.assertEqual(time_blocks, predicted_time_blocks)

    # Ensures that the proper time blocks are returned when one course with start/end times is present on Tth,
    # but now specifying to look in several buildings
    def test_tth_time_blocks_with_single_course_multiple_buildings(self):
        self.create_simp_tth_course(datetime.time(hour=8, minute=00), datetime.time(hour=9, minute=15))
        time_blocks = services.calculate_time_blocks(["SIMP", "STCH"])
        predicted_time_blocks = {
            'M': [['06:00:00', '23:59:00']],
            'T': [['06:00:00', '08:00:00'], ['08:00:00', '09:15:00'], ['09:15:00', '23:59:00']],
            'W': [['06:00:00', '23:59:00']],
            'th': [['06:00:00', '08:00:00'], ['08:00:00', '09:15:00'], ['09:15:00', '23:59:00']],
            'F': [['06:00:00', '23:59:00']]}
        self.assertEqual(time_blocks, predicted_time_blocks)

    # Ensures that the proper time blocks are returned when two classrooms with different start/end times are present
    # on Tth, but now specifying to look in several buildings
    def test_tth_time_blocks_with_multiple_different_courses_multiple_buildings(self):
        self.create_simp_tth_course(datetime.time(hour=8, minute=00), datetime.time(hour=9, minute=15))
        self.create_simp_tth_course(datetime.time(hour=9, minute=30), datetime.time(hour=10, minute=45))
        time_blocks = services.calculate_time_blocks(["SIMP", "STCH"])
        predicted_time_blocks = {'M': [['06:00:00', '23:59:00']],
                                 'T': [['06:00:00', '08:00:00'], ['08:00:00', '09:15:00'], ['09:15:00', '09:30:00'],
                                       ['09:30:00', '10:45:00'], ['10:45:00', '23:59:00']],
                                 'W': [['06:00:00', '23:59:00']],
                                 'th': [['06:00:00', '08:00:00'], ['08:00:00', '09:15:00'],
                                        ['09:15:00', '09:30:00'], ['09:30:00', '10:45:00'],
                                        ['10:45:00', '23:59:00']],
                                 'F': [['06:00:00', '23:59:00']]}
        self.assertEqual(time_blocks, predicted_time_blocks)

    # Ensures that the proper time blocks are returned when two classrooms with the same start/end times are present
    # on Tth, but now specifying to look in several buildings
    def test_tth_time_blocks_with_multiple_same_courses_multiple_buildings(self):
        self.create_simp_tth_course(datetime.time(hour=8, minute=00), datetime.time(hour=9, minute=15))
        self.create_simp_tth_course(datetime.time(hour=8, minute=00), datetime.time(hour=9, minute=15))
        time_blocks = services.calculate_time_blocks(["SIMP", "STCH"])
        predicted_time_blocks = {
            'M': [['06:00:00', '23:59:00']],
            'T': [['06:00:00', '08:00:00'], ['08:00:00', '09:15:00'], ['09:15:00', '23:59:00']],
            'W': [['06:00:00', '23:59:00']],
            'th': [['06:00:00', '08:00:00'], ['08:00:00', '09:15:00'], ['09:15:00', '23:59:00']],
            'F': [['06:00:00', '23:59:00']]}
        self.assertEqual(time_blocks, predicted_time_blocks)

    # Ensures that only the first and last times of the day are returned in time blocks when there are courses
    # present in multiple buildings, but none with time data, specifying to look in several buildings
    def test_no_time_blocks_with_courses_in_multiple_buildings(self):
        self.create_simp_mwf_course()
        self.create_STCH_course()
        time_blocks = services.calculate_time_blocks(["SIMP", "STCH"])
        predicted_time_blocks = {'M': [['06:00:00', '23:59:00']],
                                 'T': [['06:00:00', '23:59:00']],
                                 'W': [['06:00:00', '23:59:00']],
                                 'th': [['06:00:00', '23:59:00']],
                                 'F': [['06:00:00', '23:59:00']]}
        self.assertEqual(time_blocks, predicted_time_blocks)

    # Ensures that the proper time blocks are returned when two classrooms with different start/end times are present
    # on MWF in separate buildings, specifying to look in several buildings
    def test_time_blocks_with_multiple_different_courses_in_multiple_buildings(self):
        self.create_simp_tth_course(datetime.time(hour=8, minute=00), datetime.time(hour=9, minute=15))
        self.create_STCH_course(datetime.time(hour=9, minute=00), datetime.time(hour=9, minute=50))
        time_blocks = services.calculate_time_blocks(["SIMP", "STCH"])
        predicted_time_blocks = {'M': [['06:00:00', '09:00:00'], ['09:00:00', '09:50:00'], ['09:50:00', '23:59:00']],
                                 'T': [['06:00:00', '08:00:00'], ['08:00:00', '09:15:00'], ['09:15:00', '23:59:00']],
                                 'W': [['06:00:00', '09:00:00'], ['09:00:00', '09:50:00'], ['09:50:00', '23:59:00']],
                                 'th': [['06:00:00', '08:00:00'], ['08:00:00', '09:15:00'], ['09:15:00', '23:59:00']],
                                 'F': [['06:00:00', '09:00:00'], ['09:00:00', '09:50:00'], ['09:50:00', '23:59:00']]}
        self.assertEqual(time_blocks, predicted_time_blocks)

    # Ensures that the proper time blocks are returned when two courses with the same start/end times are present on
    # MWF in different buildings, looking in several buildings
    def test_time_blocks_with_multiple_courses_same_time_in_multiple_buildings(self):
        self.create_simp_mwf_course(datetime.time(hour=8, minute=00), datetime.time(hour=8, minute=50))
        self.create_STCH_course(datetime.time(hour=8, minute=00), datetime.time(hour=8, minute=50))
        time_blocks = services.calculate_time_blocks(["SIMP", "STCH"])
        predicted_time_blocks = {
            'M': [['06:00:00', '08:00:00'], ['08:00:00', '08:50:00'], ['08:50:00', '23:59:00']],
            'T': [['06:00:00', '23:59:00']],
            'W': [['06:00:00', '08:00:00'], ['08:00:00', '08:50:00'], ['08:50:00', '23:59:00']],
            'th': [['06:00:00', '23:59:00']],
            'F': [['06:00:00', '08:00:00'], ['08:00:00', '08:50:00'], ['08:50:00', '23:59:00']]}
        self.assertEqual(time_blocks, predicted_time_blocks)

    # Ensures that only the first and last times of the day are returned if an empty array is passed for buildings
    def test_time_blocks_empty_buildings(self):
        self.create_simp_mwf_course(datetime.time(hour=8, minute=00), datetime.time(hour=8, minute=50))
        self.create_simp_tth_course(datetime.time(hour=8, minute=00), datetime.time(hour=9, minute=15))
        self.create_STCH_course(datetime.time(hour=8, minute=00), datetime.time(hour=8, minute=50))
        time_blocks = services.calculate_time_blocks([])
        predicted_time_blocks = {
            'M': [['06:00:00', '23:59:00']],
            'T': [['06:00:00', '23:59:00']],
            'W': [['06:00:00', '23:59:00']],
            'th': [['06:00:00', '23:59:00']],
            'F': [['06:00:00', '23:59:00']]}
        self.assertEqual(time_blocks, predicted_time_blocks)
