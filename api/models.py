from django.db import models


class Classroom(models.Model):
    BUILDINGS = {
        "CENG": "Civil Engineering",
        "CHPL": "All Saints Chapel",
        "CUBE": "Cube",
        "EQCT": "Equine Center",
        "FSCT": "Fortin Science Center Labs",
        "GUAD": "Guadalupe Hall",
        "HAC": "Hunthausen Activity Center",
        "LYHS": "",
        "OCON": "O'Connell Hall",
        "OFCP": "Off-Campus",
        "PCCC": "Perkins Call Canine Center",
        "PECT": "PE Center",
        "SIMP": "Simperman Hall",
        "STCH": "St. Charles Hall",
        "WBAR": "Waterbarn",
    }

    name = models.CharField(max_length=8, primary_key=True)
    building = models.CharField(max_length=4, choices=BUILDINGS)
    room_num = models.IntegerField()
    occupancy = models.IntegerField()
    type = models.CharField(max_length=10)

    def __str__(self):
        return self.name


class Instructor(models.Model):
    name = models.CharField(max_length=50)
    style = models.ForeignKey(Classroom, on_delete=models.CASCADE)

    def __str__(self):
        return self.name


class Course(models.Model):
    DAYS = {
        "M": "Monday",
        "T": "Tuesday",
        "W": "Wednesday",
        "th": "Thursday",
        "MW": "Monday, Wednesday",
        "MWF": "Monday, Wednesday, Friday",
        "Tth": "Tuesday, Thursday",
    }
    name = models.CharField(max_length=15)
    classroom = models.ForeignKey(Classroom, on_delete=models.CASCADE, related_name="course_classroom")
    day = models.CharField(max_length=3, choices=DAYS)
    start_time = models.TimeField()
    end_time = models.TimeField()
    instructor = models.ForeignKey(Instructor, on_delete=models.CASCADE)
    type = models.ForeignKey(Classroom, on_delete=models.CASCADE, related_name="course_type")

    def __str__(self):
        return self.name
