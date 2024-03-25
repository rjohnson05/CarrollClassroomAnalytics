from django.db import models


class Classroom(models.Model):
    """
    Contains all ORM models for the classroom analytics software. The models for Classes, Courses, and Instructors are
    all included here.
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
    room_num = models.IntegerField()

    occupancy = models.FloatField()
    width = models.IntegerField()
    length = models.IntegerField()
    projector_num = models.IntegerField()
    features = models.CharField(max_length=255)
    notes = models.CharField(max_length=255)

    def __str__(self):
        return self.name


class Instructor(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name


class Course(models.Model):
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
    min_credits = models.FloatField()
    status = models.CharField(max_length=255)

    start_time = models.TimeField()
    end_time = models.TimeField()
    day = models.CharField(max_length=255, choices=DAYS)
    classroom = models.ForeignKey(Classroom, on_delete=models.CASCADE)

    instruction_method = models.CharField(max_length=255)
    instructor = models.CharField(max_length=255)

    enrolled = models.IntegerField()
    capacity = models.IntegerField()

    def __str__(self):
        return self.name
