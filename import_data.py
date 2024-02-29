import pandas as pd
# from django.contrib.auth.models import User
import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "carroll_classroom_analytics.settings")
django.setup()

from api.models import Classroom, Instructor, Course


def day_maker():
    if row['CSM_MONDAY'] == 'Y' and row['CSM_WEDNESDAY'] == 'Y' and row['CSM_FRIDAY'] == 'Y':
        Course.DAYS = 'MWF'
    elif row['CSM_MONDAY'] == 'Y' and row['CSM_WEDNESDAY'] == 'Y':
        Course.DAYS = 'MW'
    elif row['CSM_TUESDAY'] == 'Y' and row['CSM_THURSDAY'] == 'Y':
        Course.DAYS = 'MW'
    elif row['CSM_MONDAY'] == 'Y':
        Course.DAYS = 'M'
    elif row['CSM_TUESDAY'] == 'Y':
        Course.DAYS = 'T'
    elif row['CSM_WEDNESDAY'] == 'Y':
        Course.DAYS = 'W'
    elif row['CSM_THURSDAY'] == 'Y':
        Course.DAYS = 'th'
    else:
        Course.DAYS = ''
    return Course.DAYS


# Read CSV file into a DataFrame
csv_file_path = 'Spring2024.csv'
df = pd.read_csv(csv_file_path)

df = df.dropna(subset=['CSM_START_TIME', 'CSM_END_TIME', 'SEC_CAPACITY'])
df = df.fillna(value="Unknown", axis=0)

df['CSM_START_TIME'] = pd.to_datetime(df['CSM_START_TIME'], format='%I:%M%p').dt.strftime('%H:%M:%S')
df['CSM_END_TIME'] = pd.to_datetime(df['CSM_END_TIME'], format='%I:%M%p').dt.strftime('%H:%M:%S')

# Write the updated DataFrame back to a CSV file
df.to_csv('Spring2024_1.csv', index=False)
df = pd.read_csv('Spring2024_1.csv')

for index, row in df.iterrows():
    instructor = Instructor.objects.create(
        name=row['SEC_FACULTY_INFO'],
        style=row['CSM_INSTR_METHOD'],
    )

    classroom = Classroom.objects.create(
        name=row['CSM_ROOM'],
        building=Classroom.BUILDINGS.get(row['CSM_BLDG'], 'Unknown'),
        # building=Classroom.BUILDINGS[row['CSM_BLDG']],
        room_num=row['SEC_SYNONYM'],
        occupancy=row['SEC_CAPACITY'],
        type=row['SEC_SUBJECT'],
    )

    day_maker()
    course = Course.objects.create(
        id=row['TEST_INDEX'],
        name=row['SEC_SHORT_TITLE'],
        # classroom=row['CSM_ROOM'],
        classroom=classroom,
        day=Course.DAYS,
        # day=Course.DAYS[row['']],
        start_time=row['CSM_START_TIME'],
        end_time=row['CSM_END_TIME'],
        instructor=instructor,
        # type=instructor,
    )

    print("CSV data has been loaded into the Django database.")