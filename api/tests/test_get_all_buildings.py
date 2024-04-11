from api.services import get_all_buildings
from django.test import TestCase


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
