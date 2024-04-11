import datetime
import os

from django.test import TestCase
import pandas as pd

from api import services
from api.models import Classroom, Course, Instructor
from api.services import calculate_day_string, calculate_number_classes, get_all_buildings, get_used_classrooms, \
    calculate_classroom_time_blocks, get_classroom_courses, get_past_time, get_next_time, upload_schedule_data, \
    upload_classroom_data


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


class CalculateNumberClasses(TestCase):
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

    # Ensures that no classrooms are shown to be used if there are no courses
    def test_no_courses(self):
        actual_num_classes = calculate_number_classes()[1]
        predicted_num_classes = {'M': {'06:00:00': 0},
                                 'T': {'06:00:00': 0},
                                 'W': {'06:00:00': 0},
                                 'th': {'06:00:00': 0},
                                 'F': {'06:00:00': 0}}
        self.assertEqual(actual_num_classes, predicted_num_classes)

    # Ensures that no classrooms are shown to be used if no courses have a time
    def test_courses_no_times(self):
        self.create_simp_mwf_course()
        actual_num_classes = calculate_number_classes()[1]
        predicted_num_classes = {'M': {'06:00:00': 0},
                                 'T': {'06:00:00': 0},
                                 'W': {'06:00:00': 0},
                                 'th': {'06:00:00': 0},
                                 'F': {'06:00:00': 0}}
        self.assertEqual(actual_num_classes, predicted_num_classes)

    # Provides test for if only one course is present
    def test_one_course(self):
        self.create_simp_mwf_course(datetime.time(hour=8, minute=00), datetime.time(hour=8, minute=50))
        actual_num_classes = calculate_number_classes()[1]
        predicted_num_classes = {'M': {'06:00:00': 0, '08:00:00': 1, '08:50:00': 0},
                                 'T': {'06:00:00': 0},
                                 'W': {'06:00:00': 0, '08:00:00': 1, '08:50:00': 0},
                                 'th': {'06:00:00': 0},
                                 'F': {'06:00:00': 0, '08:00:00': 1, '08:50:00': 0}}
        self.assertEqual(actual_num_classes, predicted_num_classes)

    # Ensures that when two courses are in the time block, the number of classes is recorded as two for the time block
    def test_two_courses_same_time(self):
        self.create_simp_mwf_course(datetime.time(hour=8, minute=00), datetime.time(hour=8, minute=50))
        self.create_simp_mwf_course(datetime.time(hour=8, minute=00), datetime.time(hour=8, minute=50))
        actual_num_classes = calculate_number_classes()[1]
        predicted_num_classes = {'M': {'06:00:00': 0, '08:00:00': 1, '08:50:00': 0},
                                 'T': {'06:00:00': 0},
                                 'W': {'06:00:00': 0, '08:00:00': 1, '08:50:00': 0},
                                 'th': {'06:00:00': 0},
                                 'F': {'06:00:00': 0, '08:00:00': 1, '08:50:00': 0}}
        self.assertEqual(actual_num_classes, predicted_num_classes)

    # Ensures that multiple time blocks can be handled
    def test_two_courses_different_time(self):
        self.create_simp_mwf_course(datetime.time(hour=8, minute=00), datetime.time(hour=8, minute=50))
        self.create_simp_mwf_course(datetime.time(hour=9, minute=00), datetime.time(hour=9, minute=50))
        actual_num_classes = calculate_number_classes()[1]
        predicted_num_classes = {'M': {'06:00:00': 0, '08:00:00': 1, '08:50:00': 0, '09:00:00': 1, '09:50:00': 0},
                                 'T': {'06:00:00': 0},
                                 'W': {'06:00:00': 0, '08:00:00': 1, '08:50:00': 0, '09:00:00': 1, '09:50:00': 0},
                                 'th': {'06:00:00': 0},
                                 'F': {'06:00:00': 0, '08:00:00': 1, '08:50:00': 0, '09:00:00': 1, '09:50:00': 0}}
        self.assertEqual(actual_num_classes, predicted_num_classes)

    # Ensures that no classrooms are shown to be used for a single building if there are no courses
    def test_no_courses_one_building(self):
        actual_num_classes = calculate_number_classes(["SIMP"])[1]
        predicted_num_classes = {'M': {'06:00:00': 0},
                                 'T': {'06:00:00': 0},
                                 'W': {'06:00:00': 0},
                                 'th': {'06:00:00': 0},
                                 'F': {'06:00:00': 0}}
        self.assertEqual(actual_num_classes, predicted_num_classes)

    # Ensures that no classrooms are shown to be used for a single classroom if no courses have a time
    def test_courses_no_times_one_building(self):
        self.create_simp_mwf_course()
        actual_num_classes = calculate_number_classes(["SIMP"])[1]
        predicted_num_classes = {'M': {'06:00:00': 0},
                                 'T': {'06:00:00': 0},
                                 'W': {'06:00:00': 0},
                                 'th': {'06:00:00': 0},
                                 'F': {'06:00:00': 0}}
        self.assertEqual(actual_num_classes, predicted_num_classes)

    # Ensures that one classroom is recorded as being used for a single classroom for the correct time slot when there is a single course
    def test_one_course_one_building(self):
        self.create_simp_mwf_course(datetime.time(hour=8, minute=00), datetime.time(hour=8, minute=50))
        actual_num_classes = calculate_number_classes(["SIMP"])[1]
        predicted_num_classes = {'M': {'06:00:00': 0, '08:00:00': 1, '08:50:00': 0},
                                 'T': {'06:00:00': 0},
                                 'W': {'06:00:00': 0, '08:00:00': 1, '08:50:00': 0},
                                 'th': {'06:00:00': 0},
                                 'F': {'06:00:00': 0, '08:00:00': 1, '08:50:00': 0}}
        self.assertEqual(actual_num_classes, predicted_num_classes)

    # Ensures that when two courses are in the time block, the number of classes for a single building is recorded as two for the time block
    def test_two_courses_same_time_one_building(self):
        self.create_simp_mwf_course(datetime.time(hour=8, minute=00), datetime.time(hour=8, minute=50))
        self.create_simp_mwf_course(datetime.time(hour=8, minute=00), datetime.time(hour=8, minute=50))
        actual_num_classes = calculate_number_classes(["SIMP"])[1]
        predicted_num_classes = {'M': {'06:00:00': 0, '08:00:00': 1, '08:50:00': 0},
                                 'T': {'06:00:00': 0},
                                 'W': {'06:00:00': 0, '08:00:00': 1, '08:50:00': 0},
                                 'th': {'06:00:00': 0},
                                 'F': {'06:00:00': 0, '08:00:00': 1, '08:50:00': 0}}
        self.assertEqual(actual_num_classes, predicted_num_classes)

    # Ensures that multiple time blocks can be handled when looking in a single building
    def test_two_courses_different_time_one_building(self):
        self.create_simp_mwf_course(datetime.time(hour=8, minute=00), datetime.time(hour=8, minute=50))
        self.create_simp_mwf_course(datetime.time(hour=9, minute=00), datetime.time(hour=9, minute=50))
        actual_num_classes = calculate_number_classes(["SIMP"])[1]
        predicted_num_classes = {'M': {'06:00:00': 0, '08:00:00': 1, '08:50:00': 0, '09:00:00': 1, '09:50:00': 0},
                                 'T': {'06:00:00': 0},
                                 'W': {'06:00:00': 0, '08:00:00': 1, '08:50:00': 0, '09:00:00': 1, '09:50:00': 0},
                                 'th': {'06:00:00': 0},
                                 'F': {'06:00:00': 0, '08:00:00': 1, '08:50:00': 0, '09:00:00': 1, '09:50:00': 0}}
        self.assertEqual(actual_num_classes, predicted_num_classes)

    # Ensure that only the classrooms being used in the specified building are shown
    def test_two_courses_one_building_not_included(self):
        self.create_simp_mwf_course(datetime.time(hour=8, minute=00), datetime.time(hour=8, minute=50))
        self.create_STCH_course(datetime.time(hour=9, minute=00), datetime.time(hour=9, minute=50))
        actual_num_classes = calculate_number_classes(["SIMP"])[1]
        predicted_num_classes = {'M': {'06:00:00': 0, '08:00:00': 1, '08:50:00': 0},
                                 'T': {'06:00:00': 0},
                                 'W': {'06:00:00': 0, '08:00:00': 1, '08:50:00': 0},
                                 'th': {'06:00:00': 0},
                                 'F': {'06:00:00': 0, '08:00:00': 1, '08:50:00': 0}}
        self.assertEqual(actual_num_classes, predicted_num_classes)

    # When an empty building list is passed, ensures that no classrooms are reported as used
    def test_no_courses_no_building(self):
        actual_num_classes = calculate_number_classes([])[1]
        predicted_num_classes = {'M': {'06:00:00': 0},
                                 'T': {'06:00:00': 0},
                                 'W': {'06:00:00': 0},
                                 'th': {'06:00:00': 0},
                                 'F': {'06:00:00': 0}}
        self.assertEqual(actual_num_classes, predicted_num_classes)

    # When an empty building list is passed, ensures that no classrooms are reported as used, even with courses present (with no times)
    def test_courses_no_times_no_building(self):
        self.create_simp_mwf_course()
        actual_num_classes = calculate_number_classes([])[1]
        predicted_num_classes = {'M': {'06:00:00': 0},
                                 'T': {'06:00:00': 0},
                                 'W': {'06:00:00': 0},
                                 'th': {'06:00:00': 0},
                                 'F': {'06:00:00': 0}}
        self.assertEqual(actual_num_classes, predicted_num_classes)

    # When an empty building list is passed, ensures that no classrooms are reported as used, even with a course assigned a time
    def test_one_course_no_building(self):
        self.create_simp_mwf_course(datetime.time(hour=8, minute=00), datetime.time(hour=8, minute=50))
        actual_num_classes = calculate_number_classes([])[1]
        predicted_num_classes = {'M': {'06:00:00': 0},
                                 'T': {'06:00:00': 0},
                                 'W': {'06:00:00': 0},
                                 'th': {'06:00:00': 0},
                                 'F': {'06:00:00': 0}}
        self.assertEqual(actual_num_classes, predicted_num_classes)

    # When an empty building list is passed, ensures that no classrooms are reported as used, even with several courses assigned a time
    def test_two_courses_same_time_no_building(self):
        self.create_simp_mwf_course(datetime.time(hour=8, minute=00), datetime.time(hour=8, minute=50))
        self.create_simp_mwf_course(datetime.time(hour=8, minute=00), datetime.time(hour=8, minute=50))
        actual_num_classes = calculate_number_classes([])[1]
        predicted_num_classes = {'M': {'06:00:00': 0},
                                 'T': {'06:00:00': 0},
                                 'W': {'06:00:00': 0},
                                 'th': {'06:00:00': 0},
                                 'F': {'06:00:00': 0}}
        self.assertEqual(actual_num_classes, predicted_num_classes)

    # Ensures that when classrooms are in use during the same time block, it is returned for the correct time block
    def test_two_classrooms_used_same_time(self):
        self.create_simp_mwf_course(datetime.time(hour=8, minute=00), datetime.time(hour=8, minute=50))
        self.create_STCH_course(datetime.time(hour=8, minute=00), datetime.time(hour=8, minute=50))
        actual_num_classes = calculate_number_classes()[1]
        predicted_num_classes = {'M': {'06:00:00': 0, '08:00:00': 2, '08:50:00': 0},
                                 'T': {'06:00:00': 0},
                                 'W': {'06:00:00': 0, '08:00:00': 2, '08:50:00': 0},
                                 'th': {'06:00:00': 0},
                                 'F': {'06:00:00': 0, '08:00:00': 2, '08:50:00': 0}}
        self.assertEqual(actual_num_classes, predicted_num_classes)

    # Ensures that when classrooms are in use during separate time blocks, they are returned for the correct time blocks
    def test_two_classrooms_used_different_times(self):
        self.create_simp_mwf_course(datetime.time(hour=8, minute=00), datetime.time(hour=8, minute=50))
        self.create_STCH_course(datetime.time(hour=9, minute=00), datetime.time(hour=9, minute=50))
        actual_num_classes = calculate_number_classes()[1]
        predicted_num_classes = {'M': {'06:00:00': 0, '08:00:00': 1, '08:50:00': 0, '09:00:00': 1, '09:50:00': 0},
                                 'T': {'06:00:00': 0},
                                 'W': {'06:00:00': 0, '08:00:00': 1, '08:50:00': 0, '09:00:00': 1, '09:50:00': 0},
                                 'th': {'06:00:00': 0},
                                 'F': {'06:00:00': 0, '08:00:00': 1, '08:50:00': 0, '09:00:00': 1, '09:50:00': 0}}
        self.assertEqual(actual_num_classes, predicted_num_classes)


class TestGetAllBuildings(TestCase):
    def test_get_all_buildings(self):
        actual_buildings_list = get_all_buildings()
        predicted_buildings_list = {
            "": "",
            "CENG": "Civil Engineering",
            "CHPL": "All Saints Chapel",
            "CUBE": "Cube",
            "EQCT": "Equine Center",
            "FSCT": "Fortin Science Center Labs",
            "GUAD": "Guadalupe Hall",
            "HAC": "Hunthausen Activity Center",
            "OCON": "O'Connell Hall",
            "OFCP": "Off-Campus",
            "PCCC": "Perkins Call Canine Center",
            "PECT": "PE Center",
            "SIMP": "Simperman Hall",
            "STCH": "St. Charles Hall",
            "WBAR": "Waterbarn",
        }
        self.assertEqual(actual_buildings_list, predicted_buildings_list)


class TestGetUsedClassrooms(TestCase):
    # Creates a MWF course in SIMP at the designated start/end time
    @classmethod
    def create_simp_course(cls, start_time=None, end_time=None, building="SIMP", room_num="120"):
        classroom = Classroom.objects.get(name=building + "-" + room_num)
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

    # Creates a MWF course with a null classroom at the designated start/end time
    @classmethod
    def create_null_course(cls, start_time=None, end_time=None):
        classroom = None
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

    # Creates a MWF course with an OFCP classroom at the designated start/end time
    @classmethod
    def create_ofcp_course(cls, start_time=None, end_time=None):
        classroom = Classroom.objects.get(name="OFCP-OFCP")
        instructor = Instructor.objects.get(name="Brent Northup")

        Course.objects.create(
            section_id=1,
            course_num="123",
            section_num="A",
            term="2024SPR",
            start_date=datetime.date(2024, 4, 4),
            end_date=datetime.date(2024, 4, 5),
            name="Nursing Clinical",
            subject="NU",
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
            name="SIMP-121",
            building="SIMP",
            room_num="121"
        )
        Classroom.objects.create(
            name="STCH-120",
            building="STCH",
            room_num="120"
        )
        Classroom.objects.create(
            name="OFCP-OFCP",
            building="OFCP",
            room_num="OFCP"
        )


    # Ensures that no classrooms are found if there are no courses
    def test_no_courses(self):
        actual_classrooms = get_used_classrooms('M', '08:00:00', '08:50:00')
        predicted_classrooms = {}
        self.assertEqual(actual_classrooms, predicted_classrooms)

    # Ensures that no classrooms are found if the day provided is invalid
    def test_invalid_day(self):
        actual_classrooms = get_used_classrooms('wrong', '08:00:00', '08:50:00')
        predicted_classrooms = {}
        self.assertEqual(actual_classrooms, predicted_classrooms)

    # Ensures that no classrooms are found if the start time provided is invalid
    def test_invalid_start_time(self):
        actual_classrooms = get_used_classrooms('M', 'wrong', '08:50:00')
        predicted_classrooms = {}
        self.assertEqual(actual_classrooms, predicted_classrooms)

    # Ensures that no classrooms are found if the end time provided is invalid
    def test_invalid_end_time(self):
        actual_classrooms = get_used_classrooms('M', '08:00:00', 'wrong')
        predicted_classrooms = {}
        self.assertEqual(actual_classrooms, predicted_classrooms)

    # Ensures that no classrooms are found if the buildings list provided is invalid
    def test_invalid_buildings(self):
        actual_classrooms = get_used_classrooms('M', '08:00:00', '08:50:00', 'wrong')
        predicted_classrooms = {}
        self.assertEqual(actual_classrooms, predicted_classrooms)

    # Ensures that no classrooms are found if an empty buildings string is provided
    def test_empty_buildings(self):
        actual_classrooms = get_used_classrooms('M', 'wrong', '08:50:00', "")
        predicted_classrooms = {}
        self.assertEqual(actual_classrooms, predicted_classrooms)

    # Ensures that no classrooms are returned if none are used during the specified time block
    def test_no_classroom_used_all_buildings(self):
        actual_classrooms = get_used_classrooms('M', '09:00:00', '09:50:00')
        predicted_classrooms = {}
        self.assertEqual(actual_classrooms, predicted_classrooms)

    # Ensures that only the single classroom used during the specified time block is returned
    def test_one_classroom_used_all_buildings(self):
        self.create_simp_course(datetime.time(hour=8, minute=00), datetime.time(hour=8, minute=50))
        self.create_STCH_course(datetime.time(hour=9, minute=00), datetime.time(hour=9, minute=50))
        classroom = Classroom.objects.get(name="SIMP-120")
        course = Course.objects.get(name="Advanced Software Engineering")

        actual_classrooms = get_used_classrooms('M', '08:00:00', '08:50:00')
        predicted_classrooms = {
            classroom.name: [[course.name, course.instructor, course.classroom.occupancy, course.enrolled]]}
        self.assertEqual(actual_classrooms, predicted_classrooms)

    # Ensures that several classrooms are returned if both are in the specified time block
    def test_two_classroom_used_all_buildings(self):
        self.create_simp_course(datetime.time(hour=8, minute=00), datetime.time(hour=8, minute=50))
        self.create_STCH_course(datetime.time(hour=8, minute=00), datetime.time(hour=8, minute=50))
        classroom1 = Classroom.objects.get(name="SIMP-120")
        classroom2 = Classroom.objects.get(name="STCH-120")
        course1 = Course.objects.get(name="Advanced Software Engineering")
        course2 = Course.objects.get(name="Small Group Communication")

        actual_classrooms = get_used_classrooms('M', '08:00:00', '08:50:00')
        predicted_classrooms = {
            classroom1.name: [[course1.name, course1.instructor, course1.classroom.occupancy, course1.enrolled]],
            classroom2.name: [[course2.name, course2.instructor, course2.classroom.occupancy, course2.enrolled]]}
        self.assertEqual(actual_classrooms, predicted_classrooms)

    # Ensures that no classrooms are returned if none are used in the specified building
    def test_no_classroom_used_one_building(self):
        actual_classrooms = get_used_classrooms('M', '08:00:00', '08:50:00', ["SIMP"])
        predicted_classrooms = {}
        self.assertEqual(actual_classrooms, predicted_classrooms)

    # Ensures that the single classroom used in the specified building is returned
    def test_one_classroom_used_one_building(self):
        self.create_simp_course(datetime.time(hour=8, minute=00), datetime.time(hour=8, minute=50))
        classroom = Classroom.objects.get(name="SIMP-120")
        course = Course.objects.get(name="Advanced Software Engineering")

        actual_classrooms = get_used_classrooms('M', '08:00:00', '08:50:00', ["SIMP"])
        predicted_classrooms = {
            classroom.name: [[course.name, course.instructor, course.classroom.occupancy, course.enrolled]]}
        self.assertEqual(actual_classrooms, predicted_classrooms)

    # Ensures that both classrooms used in the specified building are returned
    def test_two_classrooms_used_one_building(self):
        self.create_simp_course(datetime.time(hour=8, minute=00), datetime.time(hour=8, minute=50))
        self.create_simp_course(datetime.time(hour=8, minute=00), datetime.time(hour=8, minute=50), "SIMP", "121")
        classroom1 = Classroom.objects.get(name="SIMP-120")
        classroom2 = Classroom.objects.get(name="SIMP-121")
        course1 = Course.objects.get(name="Advanced Software Engineering", classroom__name='SIMP-120')
        course2 = Course.objects.get(name="Advanced Software Engineering", classroom__name='SIMP-121')

        actual_classrooms = get_used_classrooms('M', '08:00:00', '08:50:00', ["SIMP"])
        predicted_classrooms = {
            classroom1.name: [[course1.name, course1.instructor, course1.classroom.occupancy, course1.enrolled]],
            classroom2.name: [[course2.name, course2.instructor, course2.classroom.occupancy, course2.enrolled]]}
        self.assertEqual(actual_classrooms, predicted_classrooms)

    # Ensures that no classrooms are returned when there are none used within the specified two buildings
    def test_no_classroom_used_two_buildings(self):
        self.create_simp_course(datetime.time(hour=8, minute=00), datetime.time(hour=8, minute=50))
        self.create_simp_course(datetime.time(hour=9, minute=00), datetime.time(hour=9, minute=50), "SIMP", "121")

        actual_classrooms = get_used_classrooms('M', '10:00:00', '10:50:00', ["SIMP", "STCH"])
        predicted_classrooms = {}
        self.assertEqual(actual_classrooms, predicted_classrooms)

    # Ensures that the only classroom within the specified bounds (within two buildings) is returned
    def test_one_classroom_used_two_buildings(self):
        self.create_simp_course(datetime.time(hour=8, minute=00), datetime.time(hour=8, minute=50))
        classroom1 = Classroom.objects.get(name="SIMP-120")
        course1 = Course.objects.get(name="Advanced Software Engineering")

        actual_classrooms = get_used_classrooms('M', '08:00:00', '08:50:00', ["SIMP", "STCH"])
        predicted_classrooms = {
            classroom1.name: [[course1.name, course1.instructor, course1.classroom.occupancy, course1.enrolled]]}
        self.assertEqual(actual_classrooms, predicted_classrooms)

    # Ensures that both classrooms are returned when two buildings are specified
    def test_two_classrooms_used_two_buildings(self):
        self.create_simp_course(datetime.time(hour=8, minute=00), datetime.time(hour=8, minute=50))
        self.create_STCH_course(datetime.time(hour=8, minute=00), datetime.time(hour=8, minute=50))
        classroom1 = Classroom.objects.get(name="SIMP-120")
        classroom2 = Classroom.objects.get(name="STCH-120")
        course1 = Course.objects.get(name="Advanced Software Engineering")
        course2 = Course.objects.get(name="Small Group Communication")

        actual_classrooms = get_used_classrooms('M', '08:00:00', '08:50:00', ["SIMP", "STCH"])
        predicted_classrooms = {
            classroom1.name: [[course1.name, course1.instructor, course1.classroom.occupancy, course1.enrolled]],
            classroom2.name: [[course2.name, course2.instructor, course2.classroom.occupancy, course2.enrolled]]}
        self.assertEqual(actual_classrooms, predicted_classrooms)

    # Ensures that a course with a null classroom returns no results
    def test_null_classroom_course_all_buildings(self):
        self.create_null_course(datetime.time(hour=8, minute=00), datetime.time(hour=8, minute=50))
        actual_classrooms = get_used_classrooms('M', '08:00:00', '08:50:00')
        predicted_classrooms = {}
        self.assertEqual(actual_classrooms, predicted_classrooms)

    # Ensures that a null classroom is not listed when a building is specified
    def test_null_classroom_course_one_building(self):
        self.create_null_course(datetime.time(hour=8, minute=00), datetime.time(hour=8, minute=50))
        actual_classrooms = get_used_classrooms('M', '08:00:00', '08:50:00', "SIMP")
        predicted_classrooms = {}
        self.assertEqual(actual_classrooms, predicted_classrooms)

    # Ensures that OFCP courses are not returned
    def test_ofcp_classroom_course_all_buildings(self):
        self.create_ofcp_course(datetime.time(hour=8, minute=00), datetime.time(hour=8, minute=50))
        actual_classrooms = get_used_classrooms('M', '08:00:00', '08:50:00')
        predicted_classrooms = {}
        self.assertEqual(actual_classrooms, predicted_classrooms)

    # Ensures that OFCP courses are not returned, even when buildings are specified
    def test_ofcp_classroom_course_one_building(self):
        self.create_ofcp_course(datetime.time(hour=8, minute=00), datetime.time(hour=8, minute=50))
        actual_classrooms = get_used_classrooms('M', '08:00:00', '08:50:00', "SIMP")
        predicted_classrooms = {}
        self.assertEqual(actual_classrooms, predicted_classrooms)


class CalculateClassroomTimeBlocks(TestCase):
    # Creates a MWF course in SIMP at the designated start/end time
    @classmethod
    def create_simp_course(cls, start_time=None, end_time=None, building="SIMP", room_num="120"):
        classroom = Classroom.objects.get(name=building + "-" + room_num)
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
            name="SIMP-121",
            building="SIMP",
            room_num="121"
        )
        Classroom.objects.create(
            name="STCH-120",
            building="STCH",
            room_num="120"
        )
        Classroom.objects.create(
            name="OFCP-OFCP",
            building="OFCP",
            room_num="OFCP"
        )

    # Ensures that a classroom with no courses returns only the first and last day times
    def test_empty_classroom(self):
        actual_blocks = calculate_classroom_time_blocks("SIMP-120")
        predicted_blocks = {'M': [['06:00:00', '23:59:00']],
                            'T': [['06:00:00', '23:59:00']],
                            'W': [['06:00:00', '23:59:00']],
                            'th': [['06:00:00', '23:59:00']],
                            'F': [['06:00:00', '23:59:00']]}
        self.assertEqual(actual_blocks, predicted_blocks)

    # Ensure that a classroom with course returns the time blocks for that course
    def test_one_course(self):
        self.create_simp_course(datetime.time(hour=8, minute=00), datetime.time(hour=8, minute=50))
        actual_blocks = calculate_classroom_time_blocks("SIMP-120")
        predicted_blocks = {'M': [['06:00:00', '08:00:00'], ['08:00:00', '08:50:00'], ['08:50:00', '23:59:00']],
                            'T': [['06:00:00', '23:59:00']],
                            'W': [['06:00:00', '08:00:00'], ['08:00:00', '08:50:00'], ['08:50:00', '23:59:00']],
                            'th': [['06:00:00', '23:59:00']],
                            'F': [['06:00:00', '08:00:00'], ['08:00:00', '08:50:00'], ['08:50:00', '23:59:00']]}
        self.assertEqual(actual_blocks, predicted_blocks)

    # Ensure that a course from a different classroom than the one specified is not returned
    def test_one_course_different_classroom(self):
        self.create_simp_course(datetime.time(hour=8, minute=00), datetime.time(hour=8, minute=50))
        actual_blocks = calculate_classroom_time_blocks("STCH-120")
        predicted_blocks = {'M': [['06:00:00', '23:59:00']],
                            'T': [['06:00:00', '23:59:00']],
                            'W': [['06:00:00', '23:59:00']],
                            'th': [['06:00:00', '23:59:00']],
                            'F': [['06:00:00', '23:59:00']]}
        self.assertEqual(actual_blocks, predicted_blocks)

    # Ensure that the time blocks from two courses in a single classroom are returned
    def test_two_courses(self):
        self.create_simp_course(datetime.time(hour=8, minute=00), datetime.time(hour=8, minute=50))
        self.create_simp_course(datetime.time(hour=9, minute=00), datetime.time(hour=9, minute=50))
        actual_blocks = calculate_classroom_time_blocks("SIMP-120")
        predicted_blocks = {'M': [['06:00:00', '08:00:00'], ['08:00:00', '08:50:00'], ['08:50:00', '09:00:00'], ['09:00:00', '09:50:00'], ['09:50:00', '23:59:00']],
                            'T': [['06:00:00', '23:59:00']],
                            'W': [['06:00:00', '08:00:00'], ['08:00:00', '08:50:00'], ['08:50:00', '09:00:00'], ['09:00:00', '09:50:00'], ['09:50:00', '23:59:00']],
                            'th': [['06:00:00', '23:59:00']],
                            'F': [['06:00:00', '08:00:00'], ['08:00:00', '08:50:00'], ['08:50:00', '09:00:00'], ['09:00:00', '09:50:00'], ['09:50:00', '23:59:00']]}
        self.assertEqual(actual_blocks, predicted_blocks)

    # Ensure that only the course from the specified classroom is returned
    def test_two_courses_different_classrooms(self):
        self.create_simp_course(datetime.time(hour=8, minute=00), datetime.time(hour=8, minute=50))
        self.create_STCH_course(datetime.time(hour=9, minute=00), datetime.time(hour=9, minute=50))
        actual_blocks = calculate_classroom_time_blocks("SIMP-120")
        predicted_blocks = {'M': [['06:00:00', '08:00:00'], ['08:00:00', '08:50:00'], ['08:50:00', '23:59:00']],
                            'T': [['06:00:00', '23:59:00']],
                            'W': [['06:00:00', '08:00:00'], ['08:00:00', '08:50:00'], ['08:50:00', '23:59:00']],
                            'th': [['06:00:00', '23:59:00']],
                            'F': [['06:00:00', '08:00:00'], ['08:00:00', '08:50:00'], ['08:50:00', '23:59:00']]}
        self.assertEqual(actual_blocks, predicted_blocks)

    # Ensure that only the first and last time blocks are returned when an invalid classroom name is given
    def test_invalid_classroom_name(self):
        self.create_simp_course(datetime.time(hour=8, minute=00), datetime.time(hour=8, minute=50))
        actual_blocks = calculate_classroom_time_blocks("test")
        predicted_blocks = {'M': [['06:00:00', '23:59:00']],
                            'T': [['06:00:00', '23:59:00']],
                            'W': [['06:00:00', '23:59:00']],
                            'th': [['06:00:00', '23:59:00']],
                            'F': [['06:00:00', '23:59:00']]}
        self.assertEqual(actual_blocks, predicted_blocks)


class GetClassroomCourses(TestCase):
    # Creates a MWF course in SIMP at the designated start/end time
    @classmethod
    def create_simp_course(cls, start_time=None, end_time=None, building="SIMP", room_num="120"):
        classroom = Classroom.objects.get(name=building + "-" + room_num)
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
            name="SIMP-121",
            building="SIMP",
            room_num="121"
        )
        Classroom.objects.create(
            name="STCH-120",
            building="STCH",
            room_num="120"
        )
        Classroom.objects.create(
            name="OFCP-OFCP",
            building="OFCP",
            room_num="OFCP"
        )

    # Ensure that no courses are returned for an emtpy classroom
    def test_empty_classroom(self):
        classroom = Classroom.objects.get(name="SIMP-120")
        actual_courses = get_classroom_courses(classroom)[1]
        predicted_courses = {'M': {'06:00:00': ['', '', 0]},
                             'T': {'06:00:00': ['', '', 0]},
                             'W': {'06:00:00': ['', '', 0]},
                             'th': {'06:00:00': ['', '', 0]},
                             'F': {'06:00:00': ['', '', 0]}}
        self.assertEqual(actual_courses, predicted_courses)

    # Ensure that only a single course is returned for a single classroom when it only houses one course
    def test_one_course(self):
        self.create_simp_course(datetime.time(hour=8, minute=00), datetime.time(hour=8, minute=50))
        course = Course.objects.get(name="Advanced Software Engineering")

        actual_courses = get_classroom_courses("SIMP-120")[1]
        predicted_courses = {
            'M': {'06:00:00': ['', '', 0], '08:00:00': [[course.name, course.instructor, course.enrolled]],
                  '08:50:00': ['', '', 0]},
            'T': {'06:00:00': ['', '', 0]},
            'W': {'06:00:00': ['', '', 0], '08:00:00': [[course.name, course.instructor, course.enrolled]],
                  '08:50:00': ['', '', 0]},
            'th': {'06:00:00': ['', '', 0]},
            'F': {'06:00:00': ['', '', 0], '08:00:00': [[course.name, course.instructor, course.enrolled]], '08:50:00': ['', '', 0]}}
        self.assertEqual(actual_courses, predicted_courses)

    # Ensure that a course being taught in classroom different from the one specified is not returned
    def test_one_course_different_classroom(self):
        self.create_simp_course(datetime.time(hour=8, minute=00), datetime.time(hour=8, minute=50))

        actual_courses = get_classroom_courses("STCH-120")[1]
        predicted_courses = {
            'M': {'06:00:00': ['', '', 0]},
            'T': {'06:00:00': ['', '', 0]},
            'W': {'06:00:00': ['', '', 0]},
            'th': {'06:00:00': ['', '', 0]},
            'F': {'06:00:00': ['', '', 0]}}
        self.assertEqual(actual_courses, predicted_courses)

    # Ensure that two courses in the same classroom are both returned
    def test_two_courses(self):
        self.create_simp_course(datetime.time(hour=8, minute=00), datetime.time(hour=8, minute=50))
        self.create_simp_course(datetime.time(hour=9, minute=00), datetime.time(hour=9, minute=50))
        course1 = Course.objects.get(name="Advanced Software Engineering", start_time='08:00:00')
        course2 = Course.objects.get(name="Advanced Software Engineering", start_time='09:00:00')

        actual_courses = get_classroom_courses("SIMP-120")[1]
        predicted_courses = {
            'M': {'06:00:00': ["", "", 0], '08:00:00': [[course1.name, course1.instructor, course1.enrolled]],
                  '08:50:00': ["", "", 0], '09:00:00': [[course2.name, course2.instructor, course2.enrolled]],
                  '09:50:00': ["", "", 0]},
            'T': {'06:00:00': ["", "", 0]},
            'W': {'06:00:00': ["", "", 0], '08:00:00': [[course1.name, course1.instructor, course1.enrolled]],
                  '08:50:00': ["", "", 0], '09:00:00': [[course2.name, course2.instructor, course2.enrolled]],
                  '09:50:00': ["", "", 0]},
            'th': {'06:00:00': ["", "", 0]},
            'F': {'06:00:00': ["", "", 0], '08:00:00': [[course1.name, course1.instructor, course1.enrolled]],
                  '08:50:00': ["", "", 0], '09:00:00': [[course2.name, course2.instructor, course2.enrolled]],
                  '09:50:00': ["", "", 0]}}
        self.assertEqual(actual_courses, predicted_courses)

    # Ensure that no courses are returned if an invalid classroom name is given
    def test_invalid_classroom_name(self):
        actual_courses = get_classroom_courses("test")[1]
        predicted_courses = {
            'M': {'06:00:00': ['', '', 0]},
            'T': {'06:00:00': ['', '', 0]},
            'W': {'06:00:00': ['', '', 0]},
            'th': {'06:00:00': ['', '', 0]},
            'F': {'06:00:00': ['', '', 0]}}
        self.assertEqual(actual_courses, predicted_courses)


class GetPastTime(TestCase):
    # Creates a MWF course in SIMP at the designated start/end time
    @classmethod
    def create_simp_course(cls, start_time=None, end_time=None, building="SIMP", room_num="120"):
        classroom = Classroom.objects.get(name=building + "-" + room_num)
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
            name="SIMP-121",
            building="SIMP",
            room_num="121"
        )
        Classroom.objects.create(
            name="STCH-120",
            building="STCH",
            room_num="120"
        )
        Classroom.objects.create(
            name="OFCP-OFCP",
            building="OFCP",
            room_num="OFCP"
        )

    # Ensure that the first time slot of the day is returned if there are no course times between the first/last times of the day
    def test_no_courses(self):
        actual_past_time = get_past_time('M', '23:59:00')
        predicted_past_time = '06:00'
        self.assertEqual(actual_past_time, predicted_past_time)

    # Ensure that the correct past time is returned when one course exists
    def test_no_buildings(self):
        self.create_simp_course(datetime.time(hour=8, minute=00), datetime.time(hour=8, minute=50))
        actual_past_time = get_past_time('M', '23:59:00')
        predicted_past_time = '08:50'
        self.assertEqual(actual_past_time, predicted_past_time)

    # Ensure that the first time of the day is returned if the building list is empty
    def test_empty_buildings(self):
        self.create_simp_course(datetime.time(hour=8, minute=00), datetime.time(hour=8, minute=50))
        actual_past_time = get_past_time('M', '23:59:00', [])
        predicted_past_time = '06:00'
        self.assertEqual(actual_past_time, predicted_past_time)

    # Ensure that the correct past time is returned when a single building is specified
    def test_one_building(self):
        self.create_simp_course(datetime.time(hour=8, minute=00), datetime.time(hour=8, minute=50))
        actual_past_time = get_past_time('M', '23:59:00', ["SIMP"])
        predicted_past_time = '08:50'
        self.assertEqual(actual_past_time, predicted_past_time)

    # Ensure that the correct past time is returned when two building is specified
    def test_two_buildings(self):
        self.create_simp_course(datetime.time(hour=8, minute=00), datetime.time(hour=8, minute=50))
        actual_past_time = get_past_time('M', '23:59:00', ["SIMP", "STCH"])
        predicted_past_time = '08:50'
        self.assertEqual(actual_past_time, predicted_past_time)

    # Ensure that an empty string is returned if there is no time before the specified time
    def test_no_past_time(self):
        self.create_simp_course(datetime.time(hour=8, minute=00), datetime.time(hour=8, minute=50))
        actual_past_time = get_past_time('M', '06:00:00')
        predicted_past_time = ''
        self.assertEqual(actual_past_time, predicted_past_time)

    # Ensure that an empty string is returned if the given time is not a start/end time within the database
    def test_time_not_found(self):
        self.create_simp_course(datetime.time(hour=8, minute=00), datetime.time(hour=8, minute=50))
        actual_past_time = get_past_time('M', '09:00:00', ["SIMP"])
        predicted_past_time = ''
        self.assertEqual(actual_past_time, predicted_past_time)

    # Ensure that an empty string is returned if the given day is invalid
    def test_invalid_day(self):
        self.create_simp_course(datetime.time(hour=8, minute=00), datetime.time(hour=8, minute=50))
        actual_past_time = get_past_time('test', '23:59:00', ["SIMP"])
        predicted_past_time = ''
        self.assertEqual(actual_past_time, predicted_past_time)

    # Ensure that an empty string is returned if the given time is invalid
    def test_invalid_time(self):
        self.create_simp_course(datetime.time(hour=8, minute=00), datetime.time(hour=8, minute=50))
        actual_past_time = get_past_time('M', 'test', ["SIMP"])
        predicted_past_time = ''
        self.assertEqual(actual_past_time, predicted_past_time)

    # Ensure that the first time of the day is returned if the given building list is invalid
    def test_invalid_building(self):
        self.create_simp_course(datetime.time(hour=8, minute=00), datetime.time(hour=8, minute=50))
        actual_past_time = get_past_time('M', '23:59:00', ["test"])
        predicted_past_time = '06:00'
        self.assertEqual(actual_past_time, predicted_past_time)


class GetNextTime(TestCase):
    # Creates a MWF course in SIMP at the designated start/end time
    @classmethod
    def create_simp_course(cls, start_time=None, end_time=None, building="SIMP", room_num="120"):
        classroom = Classroom.objects.get(name=building + "-" + room_num)
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
            name="SIMP-121",
            building="SIMP",
            room_num="121"
        )
        Classroom.objects.create(
            name="STCH-120",
            building="STCH",
            room_num="120"
        )
        Classroom.objects.create(
            name="OFCP-OFCP",
            building="OFCP",
            room_num="OFCP"
        )

    # Ensure that the first time slot of the day is returned if there are no course times between the first/last times of the day
    def test_no_courses(self):
        actual_next_time = get_next_time('M', '06:00:00')
        predicted_next_time = '23:59'
        self.assertEqual(actual_next_time, predicted_next_time)

    # Ensure that the correct next time is returned when one course exists
    def test_no_buildings(self):
        self.create_simp_course(datetime.time(hour=8, minute=00), datetime.time(hour=8, minute=50))
        actual_next_time = get_next_time('M', '06:00:00')
        predicted_next_time = '08:00'
        self.assertEqual(actual_next_time, predicted_next_time)

    # Ensure that the last time of the day is returned if the building list is empty
    def test_empty_buildings(self):
        self.create_simp_course(datetime.time(hour=8, minute=00), datetime.time(hour=8, minute=50))
        actual_next_time = get_next_time('M', '06:00:00', [])
        predicted_next_time = '23:59'
        self.assertEqual(actual_next_time, predicted_next_time)

    # Ensure that the correct next time is returned when a single building is specified
    def test_one_building(self):
        self.create_simp_course(datetime.time(hour=8, minute=00), datetime.time(hour=8, minute=50))
        actual_next_time = get_next_time('M', '06:00:00', ["SIMP"])
        predicted_next_time = '08:00'
        self.assertEqual(actual_next_time, predicted_next_time)

    # Ensure that the correct next time is returned when two building is specified
    def test_two_buildings(self):
        self.create_simp_course(datetime.time(hour=8, minute=00), datetime.time(hour=8, minute=50))
        actual_next_time = get_next_time('M', '06:00:00', ["SIMP", "STCH"])
        predicted_next_time = '08:00'
        self.assertEqual(actual_next_time, predicted_next_time)

    # Ensure that an empty string is returned if there is no time before the specified time
    def test_no_past_time(self):
        self.create_simp_course(datetime.time(hour=8, minute=00), datetime.time(hour=8, minute=50))
        actual_next_time = get_next_time('M', '23:59:00')
        predicted_next_time = ''
        self.assertEqual(actual_next_time, predicted_next_time)

    # Ensure that an empty string is returned if the given time is not a start/end time within the database
    def test_time_not_found(self):
        self.create_simp_course(datetime.time(hour=8, minute=00), datetime.time(hour=8, minute=50))
        actual_next_time = get_next_time('M', '09:00:00', ["SIMP"])
        predicted_next_time = ''
        self.assertEqual(actual_next_time, predicted_next_time)

    # Ensure that an empty string is returned if the given day is invalid
    def test_invalid_day(self):
        self.create_simp_course(datetime.time(hour=8, minute=00), datetime.time(hour=8, minute=50))
        actual_next_time = get_next_time('test', '23:59:00', ["SIMP"])
        predicted_next_time = ''
        self.assertEqual(actual_next_time, predicted_next_time)

    # Ensure that an empty string is returned if the given time is invalid
    def test_invalid_time(self):
        self.create_simp_course(datetime.time(hour=8, minute=00), datetime.time(hour=8, minute=50))
        actual_next_time = get_next_time('M', 'test', ["SIMP"])
        predicted_next_time = ''
        self.assertEqual(actual_next_time, predicted_next_time)

    # Ensure that an empty string is returned if the given building list is invalid
    def test_invalid_building(self):
        self.create_simp_course(datetime.time(hour=8, minute=00), datetime.time(hour=8, minute=50))
        actual_next_time = get_next_time('M', '23:59:00', ["test"])
        predicted_next_time = ''
        self.assertEqual(actual_next_time, predicted_next_time)


class CalculateDayString(TestCase):
    def test_monday(self):
        df = pd.DataFrame({'CSM_MONDAY': ['Y'],
                           'CSM_TUESDAY': [None],
                           'CSM_WEDNESDAY': [None],
                           'CSM_THURSDAY': [None],
                           'CSM_FRIDAY': [None]})
        self.assertEqual(calculate_day_string(df.iloc[0]), 'M')

    def test_tuesday(self):
        df = pd.DataFrame({'CSM_MONDAY': [None],
                           'CSM_TUESDAY': ['Y'],
                           'CSM_WEDNESDAY': [None],
                           'CSM_THURSDAY': [None],
                           'CSM_FRIDAY': [None]})
        self.assertEqual(calculate_day_string(df.iloc[0]), 'T')

    def test_wednesday(self):
        df = pd.DataFrame({'CSM_MONDAY': [None],
                           'CSM_TUESDAY': [None],
                           'CSM_WEDNESDAY': ['Y'],
                           'CSM_THURSDAY': [None],
                           'CSM_FRIDAY': [None]})
        self.assertEqual(calculate_day_string(df.iloc[0]), 'W')

    def test_thursday(self):
        df = pd.DataFrame({'CSM_MONDAY': [None],
                           'CSM_TUESDAY': [None],
                           'CSM_WEDNESDAY': [None],
                           'CSM_THURSDAY': ['Y'],
                           'CSM_FRIDAY': [None]})
        self.assertEqual(calculate_day_string(df.iloc[0]), 'th')

    def test_friday(self):
        df = pd.DataFrame({'CSM_MONDAY': [None],
                           'CSM_TUESDAY': [None],
                           'CSM_WEDNESDAY': [None],
                           'CSM_THURSDAY': [None],
                           'CSM_FRIDAY': ['Y']})
        self.assertEqual(calculate_day_string(df.iloc[0]), 'F')

    def test_mon_tues(self):
        df = pd.DataFrame({'CSM_MONDAY': ['Y'],
                           'CSM_TUESDAY': ['Y'],
                           'CSM_WEDNESDAY': [None],
                           'CSM_THURSDAY': [None],
                           'CSM_FRIDAY': [None]})
        self.assertEqual(calculate_day_string(df.iloc[0]), 'MT')

    def test_mon_wed(self):
        df = pd.DataFrame({'CSM_MONDAY': ['Y'],
                           'CSM_TUESDAY': [None],
                           'CSM_WEDNESDAY': ['Y'],
                           'CSM_THURSDAY': [None],
                           'CSM_FRIDAY': [None]})
        self.assertEqual(calculate_day_string(df.iloc[0]), 'MW')

    def test_mon_thur(self):
        df = pd.DataFrame({'CSM_MONDAY': ['Y'],
                           'CSM_TUESDAY': [None],
                           'CSM_WEDNESDAY': [None],
                           'CSM_THURSDAY': ['Y'],
                           'CSM_FRIDAY': [None]})
        self.assertEqual(calculate_day_string(df.iloc[0]), 'Mth')

    def test_mon_fri(self):
        df = pd.DataFrame({'CSM_MONDAY': ['Y'],
                           'CSM_TUESDAY': [None],
                           'CSM_WEDNESDAY': [None],
                           'CSM_THURSDAY': [None],
                           'CSM_FRIDAY': ['Y']})
        self.assertEqual(calculate_day_string(df.iloc[0]), 'MF')

    def test_tues_wed(self):
        df = pd.DataFrame({'CSM_MONDAY': [None],
                           'CSM_TUESDAY': ['Y'],
                           'CSM_WEDNESDAY': ['Y'],
                           'CSM_THURSDAY': [None],
                           'CSM_FRIDAY': [None]})
        self.assertEqual(calculate_day_string(df.iloc[0]), 'TW')

    def test_tues_thur(self):
        df = pd.DataFrame({'CSM_MONDAY': [None],
                           'CSM_TUESDAY': ['Y'],
                           'CSM_WEDNESDAY': [None],
                           'CSM_THURSDAY': ['Y'],
                           'CSM_FRIDAY': [None]})
        self.assertEqual(calculate_day_string(df.iloc[0]), 'Tth')

    def test_tues_fri(self):
        df = pd.DataFrame({'CSM_MONDAY': [None],
                           'CSM_TUESDAY': ['Y'],
                           'CSM_WEDNESDAY': [None],
                           'CSM_THURSDAY': [None],
                           'CSM_FRIDAY': ['Y']})
        self.assertEqual(calculate_day_string(df.iloc[0]), 'TF')

    def test_wed_thur(self):
        df = pd.DataFrame({'CSM_MONDAY': [None],
                           'CSM_TUESDAY': [None],
                           'CSM_WEDNESDAY': ['Y'],
                           'CSM_THURSDAY': ['Y'],
                           'CSM_FRIDAY': [None]})
        self.assertEqual(calculate_day_string(df.iloc[0]), 'Wth')

    def test_wed_fri(self):
        df = pd.DataFrame({'CSM_MONDAY': [None],
                           'CSM_TUESDAY': [None],
                           'CSM_WEDNESDAY': ['Y'],
                           'CSM_THURSDAY': [None],
                           'CSM_FRIDAY': ['Y']})
        self.assertEqual(calculate_day_string(df.iloc[0]), 'WF')

    def test_thur_fri(self):
        df = pd.DataFrame({'CSM_MONDAY': [None],
                           'CSM_TUESDAY': [None],
                           'CSM_WEDNESDAY': [None],
                           'CSM_THURSDAY': ['Y'],
                           'CSM_FRIDAY': ['Y']})
        self.assertEqual(calculate_day_string(df.iloc[0]), 'thF')

    def test_mon_tue_wed(self):
        df = pd.DataFrame({'CSM_MONDAY': ['Y'],
                           'CSM_TUESDAY': ['Y'],
                           'CSM_WEDNESDAY': ['Y'],
                           'CSM_THURSDAY': [None],
                           'CSM_FRIDAY': [None]})
        self.assertEqual(calculate_day_string(df.iloc[0]), 'MTW')

    def test_mon_tue_thur(self):
        df = pd.DataFrame({'CSM_MONDAY': ['Y'],
                           'CSM_TUESDAY': ['Y'],
                           'CSM_WEDNESDAY': [None],
                           'CSM_THURSDAY': ['Y'],
                           'CSM_FRIDAY': [None]})
        self.assertEqual(calculate_day_string(df.iloc[0]), 'MTth')

    def test_mon_tue_fri(self):
        df = pd.DataFrame({'CSM_MONDAY': ['Y'],
                           'CSM_TUESDAY': ['Y'],
                           'CSM_WEDNESDAY': [None],
                           'CSM_THURSDAY': [None],
                           'CSM_FRIDAY': ['Y']})
        self.assertEqual(calculate_day_string(df.iloc[0]), 'MTF')

    def test_mon_wed_thu(self):
        df = pd.DataFrame({'CSM_MONDAY': ['Y'],
                           'CSM_TUESDAY': [None],
                           'CSM_WEDNESDAY': ['Y'],
                           'CSM_THURSDAY': ['Y'],
                           'CSM_FRIDAY': [None]})
        self.assertEqual(calculate_day_string(df.iloc[0]), 'MWth')

    def test_mon_wed_fri(self):
        df = pd.DataFrame({'CSM_MONDAY': ['Y'],
                           'CSM_TUESDAY': [None],
                           'CSM_WEDNESDAY': ['Y'],
                           'CSM_THURSDAY': [None],
                           'CSM_FRIDAY': ['Y']})
        self.assertEqual(calculate_day_string(df.iloc[0]), 'MWF')

    def test_mon_thu_fri(self):
        df = pd.DataFrame({'CSM_MONDAY': ['Y'],
                           'CSM_TUESDAY': [None],
                           'CSM_WEDNESDAY': [None],
                           'CSM_THURSDAY': ['Y'],
                           'CSM_FRIDAY': ['Y']})
        self.assertEqual(calculate_day_string(df.iloc[0]), 'MthF')

    def test_tue_wed_thur(self):
        df = pd.DataFrame({'CSM_MONDAY': [None],
                           'CSM_TUESDAY': ['Y'],
                           'CSM_WEDNESDAY': ['Y'],
                           'CSM_THURSDAY': ['Y'],
                           'CSM_FRIDAY': [None]})
        self.assertEqual(calculate_day_string(df.iloc[0]), 'TWth')

    def test_tue_wed_fri(self):
        df = pd.DataFrame({'CSM_MONDAY': [None],
                           'CSM_TUESDAY': ['Y'],
                           'CSM_WEDNESDAY': ['Y'],
                           'CSM_THURSDAY': [None],
                           'CSM_FRIDAY': ['Y']})
        self.assertEqual(calculate_day_string(df.iloc[0]), 'TWF')

    def test_wed_thu_fri(self):
        df = pd.DataFrame({'CSM_MONDAY': [None],
                           'CSM_TUESDAY': [None],
                           'CSM_WEDNESDAY': ['Y'],
                           'CSM_THURSDAY': ['Y'],
                           'CSM_FRIDAY': ['Y']})
        self.assertEqual(calculate_day_string(df.iloc[0]), 'WthF')

    def test_mon_tue_wed_thu(self):
        df = pd.DataFrame({'CSM_MONDAY': ['Y'],
                           'CSM_TUESDAY': ['Y'],
                           'CSM_WEDNESDAY': ['Y'],
                           'CSM_THURSDAY': ['Y'],
                           'CSM_FRIDAY': [None]})
        self.assertEqual(calculate_day_string(df.iloc[0]), 'MTWth')

    def test_mon_tue_wed_fri(self):
        df = pd.DataFrame({'CSM_MONDAY': ['Y'],
                           'CSM_TUESDAY': ['Y'],
                           'CSM_WEDNESDAY': ['Y'],
                           'CSM_THURSDAY': [None],
                           'CSM_FRIDAY': ['Y']})
        self.assertEqual(calculate_day_string(df.iloc[0]), 'MTWF')

    def test_mon_tue_thu_fri(self):
        df = pd.DataFrame({'CSM_MONDAY': ['Y'],
                           'CSM_TUESDAY': ['Y'],
                           'CSM_WEDNESDAY': [None],
                           'CSM_THURSDAY': ['Y'],
                           'CSM_FRIDAY': ['Y']})
        self.assertEqual(calculate_day_string(df.iloc[0]), 'MTthF')

    def test_mon_wed_thu_fri(self):
        df = pd.DataFrame({'CSM_MONDAY': ['Y'],
                           'CSM_TUESDAY': [None],
                           'CSM_WEDNESDAY': ['Y'],
                           'CSM_THURSDAY': ['Y'],
                           'CSM_FRIDAY': ['Y']})
        self.assertEqual(calculate_day_string(df.iloc[0]), 'MWthF')

    def test_tue_wed_thu_fri(self):
        df = pd.DataFrame({'CSM_MONDAY': [None],
                           'CSM_TUESDAY': ['Y'],
                           'CSM_WEDNESDAY': ['Y'],
                           'CSM_THURSDAY': ['Y'],
                           'CSM_FRIDAY': ['Y']})
        self.assertEqual(calculate_day_string(df.iloc[0]), 'TWthF')

    def test_mon_tue_wed_thu_fri(self):
        df = pd.DataFrame({'CSM_MONDAY': ['Y'],
                           'CSM_TUESDAY': ['Y'],
                           'CSM_WEDNESDAY': ['Y'],
                           'CSM_THURSDAY': ['Y'],
                           'CSM_FRIDAY': ['Y']})
        self.assertEqual(calculate_day_string(df.iloc[0]), 'MTWthF')


class UploadScheduleData(TestCase):
    # Ensure that a valid file can be uploaded to the database successfully
    def test_valid_upload(self):
        df = pd.DataFrame({'SEC_TERM': ['2024SP'],
                           'COURSE_SECTIONS_ID': ['20185'],
                           'SEC_STATUS': ['A'],
                           'SEC_START_DATE': ['Jan 17 2024'],
                           'SEC_END_DATE': ['Mar 10 2024'],
                           'SEC_SUBJECT': ['ACNU'],
                           'SEC_COURSE_NO': ['307'],
                           'SEC_NO': ['A'],
                           'SEC_SHORT_TITLE': ['Evd-Based Practice Rsrch'],
                           'SEC_MIN_CRED': ['3.00000'],
                           'CSM_START_TIME': ['9:00AM'],
                           'CSM_END_TIME': ['11:50AM'],
                           'CSM_MONDAY': ['-'],
                           'CSM_TUESDAY': ['Y'],
                           'CSM_WEDNESDAY': ['-'],
                           'CSM_THURSDAY': ['-'],
                           'CSM_FRIDAY': ['-'],
                           'CSM_BLDG': ['SIMP'],
                           'CSM_ROOM': ['407'],
                           'CSM_INSTR_METHOD': ['LEC'],
                           'SEC_FACULTY_INFO': ['M. Lewis'],
                           'STUDENTS_AND_RESERVED_SEATS': ['9'],
                           'SEC_CAPACITY': ['10']})
        df.to_excel('schedule.xlsx', index=False)
        upload_schedule_data('schedule.xlsx')
        os.remove('schedule.xlsx')
        course = Course.objects.get(section_id=int(df['COURSE_SECTIONS_ID'].iloc[0]))
        predicted_instructor = Instructor.objects.create(name=df['SEC_FACULTY_INFO'].iloc[0])
        predicted_classroom = Classroom.objects.create(
                name=df['CSM_BLDG'].iloc[0] + "-" + str(df['CSM_ROOM'].iloc[0]),
                building=df['CSM_BLDG'].iloc[0],
                room_num=df['CSM_ROOM'].iloc[0],
            )

        for index, row in df.iterrows():
            self.assertEqual(course.section_id, int(row['COURSE_SECTIONS_ID']))
            self.assertEqual(course.course_num, row['SEC_COURSE_NO'])
            self.assertEqual(course.section_num, row['SEC_NO'])
            self.assertEqual(course.term, row['SEC_TERM'])
            self.assertEqual(course.start_date, datetime.datetime.strptime(row['SEC_START_DATE'], '%b %d %Y').date())
            self.assertEqual(course.end_date, datetime.datetime.strptime(row['SEC_END_DATE'], '%b %d %Y').date())
            self.assertEqual(course.name, row['SEC_SHORT_TITLE'])
            self.assertEqual(course.subject, row['SEC_SUBJECT'])
            self.assertEqual(course.min_credits, float(row['SEC_MIN_CRED']))
            self.assertEqual(course.status, row['SEC_STATUS'])
            self.assertEqual(course.start_time, datetime.datetime.strptime(row['CSM_START_TIME'],'%I:%M%p').time())
            self.assertEqual(course.end_time, datetime.datetime.strptime(row['CSM_END_TIME'],'%I:%M%p').time())
            self.assertEqual(course.day, calculate_day_string(row))
            self.assertEqual(course.classroom.name, predicted_classroom.name)
            self.assertEqual(course.instruction_method, row['CSM_INSTR_METHOD'])
            self.assertEqual(course.instructor, predicted_instructor.name)
            self.assertEqual(course.enrolled, int(row['STUDENTS_AND_RESERVED_SEATS']))
            self.assertEqual(course.capacity, int(row['SEC_CAPACITY']))

    # Ensures that any file other than an Excel file will fail
    def test_invalid_file_type(self):
        df = pd.DataFrame({'SEC_TERM': ['2024SP'],
                           'COURSE_SECTIONS_ID': ['20185'],
                           'SEC_STATUS': ['A'],
                           'SEC_START_DATE': ['Jan 17 2024'],
                           'SEC_END_DATE': ['Mar 10 2024'],
                           'SEC_SUBJECT': ['ACNU'],
                           'SEC_COURSE_NO': ['307'],
                           'SEC_NO': ['A'],
                           'SEC_SHORT_TITLE': ['Evd-Based Practice Rsrch'],
                           'SEC_MIN_CRED': ['3.00000'],
                           'CSM_START_TIME': ['9:00AM'],
                           'CSM_END_TIME': ['11:50AM'],
                           'CSM_MONDAY': ['-'],
                           'CSM_TUESDAY': ['Y'],
                           'CSM_WEDNESDAY': ['-'],
                           'CSM_THURSDAY': ['-'],
                           'CSM_FRIDAY': ['-'],
                           'CSM_BLDG': ['SIMP'],
                           'CSM_ROOM': ['407'],
                           'CSM_INSTR_METHOD': ['LEC'],
                           'SEC_FACULTY_INFO': ['M. Lewis'],
                           'STUDENTS_AND_RESERVED_SEATS': ['9'],
                           'SEC_CAPACITY': ['10']})
        df.to_csv('schedule.csv', index=False, encoding='utf')
        upload_schedule_data('schedule.csv')
        os.remove('schedule.csv')
        self.assertEqual(Course.objects.all().count(), 0)

    # def test_invalid_columns(self): # For every column
    #
    # def test_null_value(self): # For every column


class UploadClassroomData(TestCase):
    # Ensure that a valid file can be uploaded to the database successfully
    def test_valid_upload(self):
        df = pd.DataFrame({'Building Information': ['SH'],
                           'Room Number': ['120'],
                           'Number of Student Seats in Room': ['15'],
                           'Width of Room': ['20'],
                           'Length of Room': ['30'],
                           'Number of Projectors in Room': ['2'],
                           'Notes': ['N/A'],
                           'Does room have any of the following?': ['N/A'],
                           'Any other things of note in Room (TV or Periodic Table poster)': ['N/A']})
        df.to_excel('classrooms.xlsx', index=False)
        upload_classroom_data('classrooms.xlsx')
        os.remove('classrooms.xlsx')

        for index, row in df.iterrows():
            classroom = Classroom.objects.get(name="SIMP-120")

            self.assertEqual(classroom.name, 'SIMP-120')
            self.assertEqual(classroom.building, 'SIMP')
            self.assertEqual(classroom.room_num, row['Room Number'])
            self.assertEqual(classroom.occupancy, float(row['Number of Student Seats in Room']))
            self.assertEqual(classroom.width, int(row['Width of Room']))
            self.assertEqual(classroom.length, int(row['Length of Room']))
            self.assertEqual(classroom.projector_num, int(row['Number of Projectors in Room']))
            self.assertEqual(classroom.features, '')
            self.assertEqual(classroom.notes, None)

    # Ensures that any file other than an Excel file will fail
    def test_invalid_file_type(self):
        df = pd.DataFrame({'Building Information': ['SH'],
                           'Room Number': ['120'],
                           'Number of Student Seats in Room': ['15'],
                           'Width of Room': ['20'],
                           'Length of Room': ['30'],
                           'Number of Projectors in Room': ['2'],
                           'Notes': ['N/A'],
                           'Does room have any of the following?': ['N/A'],
                           'Any other things of note in Room (TV or Periodic Table poster)': ['N/A']})
        df.to_csv('classrooms.csv', index=False)
        upload_schedule_data('classrooms.csv')
        os.remove('classrooms.csv')
        self.assertEqual(Classroom.objects.all().count(), 0)