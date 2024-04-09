from django.db import models

"""Contains all ORM models for the Carroll College classroom analytics software. The models for Classes, Courses, 
and Instructors are all included here.

Author: Adrian Rincon Jimenez, Ryan Johnson
"""


class Classroom(models.Model):
    """
    Holds data for a classroom object. Classrooms must have both a building and room number (which makes up the name).
    All other information is optional. Occupancy describes the number of seats in the room, and length/width describe
    the size of the room in feet. Projector_num describes the number of projectors available in the room. Features and
    notes provide any further things that should be known about the room, such as the presence of white boards or video,
    , that the room is near a fire exit, etc.
    """
    BUILDINGS = {
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

    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255)
    building = models.CharField(max_length=255, choices=BUILDINGS)
    room_num = models.CharField(max_length=255)

    occupancy = models.FloatField(default=None, blank=True, null=True)
    width = models.IntegerField(default=None, blank=True, null=True)
    length = models.IntegerField(default=None, blank=True, null=True)
    projector_num = models.IntegerField(default=None, blank=True, null=True)
    features = models.CharField(max_length=255, default=None, blank=True, null=True)
    notes = models.CharField(max_length=255, default=None, blank=True, null=True)

    def __str__(self):
        return self.name


class Instructor(models.Model):
    """
    Holds data for an instructor at Carroll College. Instructors only contain an ID and a name, being assigned to the
    course objects they teach.
    """
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name


class Course(models.Model):
    """
    Holds data for a course object. Course objects contain much information about a specific section of a Carroll
    College course. The ID is generated automatically by the ORM, while the section ID is provided by the Carroll
    registrars. The course/section number contains the numbers usually seen in the course catalog.Each course must
    contain a term, start date, and end date. The course must also have a name, subject, and status. Since not all
    courses have a defined time slot or meeting location, the start/end times and meeting location (classroom) are
    optional, as are the number of credits assigned to the course. The days of the week that the course is held on are
    represented by the days string, where each added day added an extra letter (or two) to the string. The instructor
    and instruction type for the course are listed, as are the current enrollment and capacity.
    """
    DAYS = (
        ("M", "Monday"),
        ("T", "Tuesday"),
        ("W", "Wednesday"),
        ("th", "Thursday"),
        ("MW", "Monday, Wednesday"),
        ("MWF", "Monday, Wednesday, Friday"),
        ("Tth", "Tuesday, Thursday"),
    )

    id = models.AutoField(primary_key=True)
    section_id = models.IntegerField()
    course_num = models.CharField(max_length=255)
    section_num = models.CharField(max_length=255)

    term = models.CharField(max_length=255)
    start_date = models.DateField()
    end_date = models.DateField()

    name = models.CharField(max_length=255)
    subject = models.CharField(max_length=255)
    min_credits = models.FloatField(null=True)
    status = models.CharField(max_length=255)

    start_time = models.TimeField(null=True)
    end_time = models.TimeField(null=True)
    day = models.CharField(max_length=255, choices=DAYS)
    classroom = models.ForeignKey(Classroom, on_delete=models.CASCADE, null=True)

    instruction_method = models.CharField(max_length=255)
    instructor = models.CharField(max_length=255)

    enrolled = models.IntegerField(null=True)
    capacity = models.IntegerField(null=True)

    def __str__(self):
        return self.name
