import datetime

from django.test import TestCase

from api import services
from api.models import Instructor, Classroom, Course


class CalculateTimeBlocks(TestCase):
    @classmethod
    def create_course(cls, start_time=None, end_time=None):
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

    def setUp(self):
        Instructor.objects.create(
            name="Nathan Williams"
        )
        Classroom.objects.create(
            name="SIMP-120",
            building="SIMP",
            room_num="120"
        )

    # Ensures that only the first and last times of the day are returned in time blocks when there are courses present,
    # but none with time data
    def test_no_time_blocks_with_course(self):
        self.create_course()
        time_blocks = services.calculate_time_blocks("all")
        predicted_time_blocks = {'M': [['06:00:00', '23:59:00']],
                                 'T': [['06:00:00', '23:59:00']],
                                 'W': [['06:00:00', '23:59:00']],
                                 'th': [['06:00:00', '23:59:00']],
                                 'F': [['06:00:00', '23:59:00']]}
        self.assertEqual(time_blocks, predicted_time_blocks)

    # Ensures that the proper time blocks are returned when one classroom with start/end times is present
    def test_present_time_blocks_with_course(self):
        self.create_course(datetime.time(hour=8, minute=00), datetime.time(hour=8, minute=50))
        time_blocks = services.calculate_time_blocks("all")
        predicted_time_blocks = {'M': [['06:00:00', '08:00:00'], ['08:00:00', '08:50:00'], ['08:50:00', '23:59:00']],
                                 'T': [['06:00:00', '23:59:00']],
                                 'W': [['06:00:00', '08:00:00'], ['08:00:00', '08:50:00'], ['08:50:00', '23:59:00']],
                                 'th': [['06:00:00', '23:59:00']],
                                 'F': [['06:00:00', '08:00:00'], ['08:00:00', '08:50:00'], ['08:50:00', '23:59:00']]}
        self.assertEqual(time_blocks, predicted_time_blocks)

    # Ensures that the proper time blocks are returned when two classrooms with start/end times are present
    def test_present_time_blocks_with_multiple_courses(self):
        self.create_course(datetime.time(hour=8, minute=00), datetime.time(hour=8, minute=50))
        self.create_course(datetime.time(hour=9, minute=00), datetime.time(hour=9, minute=50))
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
