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
    type = models.CharField(max_length=255)

    def __str__(self):
        return self.name


class Instructor(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255)
    style = models.CharField(max_length=255)

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
    name = models.CharField(max_length=255)
    classroom = models.ForeignKey(Classroom, on_delete=models.CASCADE)
    day = models.CharField(max_length=255, choices=DAYS)
    start_time = models.TimeField()
    end_time = models.TimeField()
    instructor = models.CharField(max_length=255)
    enrollment = models.FloatField()

    def __str__(self):
        return self.name
