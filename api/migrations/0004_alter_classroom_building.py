# Generated by Django 5.0.1 on 2024-02-26 07:32

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0003_alter_instructor_style'),
    ]

    operations = [
        migrations.AlterField(
            model_name='classroom',
            name='building',
            field=models.CharField(choices=[('CENG', 'Civil Engineering'), ('CHPL', 'All Saints Chapel'), ('CUBE', 'Cube'), ('EQCT', 'Equine Center'), ('FSCT', 'Fortin Science Center Labs'), ('GUAD', 'Guadalupe Hall'), ('HAC', 'Hunthausen Activity Center'), ('OCON', "O'Connell Hall"), ('OFCP', 'Off-Campus'), ('PCCC', 'Perkins Call Canine Center'), ('PECT', 'PE Center'), ('SIMP', 'Simperman Hall'), ('STCH', 'St. Charles Hall'), ('WBAR', 'Waterbarn')], max_length=4),
        ),
    ]