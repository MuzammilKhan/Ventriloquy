from django.test import TestCase
from wordclips.ventriloquy.ventriloquy import Ventriloquy
from wordclips.models import Wordclip


class VentriloquyTestCase(TestCase):
    def setUp(self):
        self.ventriloquy = Ventriloquy()
        # Put dummy object in databse for testing purpose
        Wordclip.objects.create(name="how")
        Wordclip.objects.create(name="are")
        Wordclip.objects.create(name="you")
        Wordclip.objects.create(name="people")


    def test_found_in_db(self):

        err, lst = self.ventriloquy.check_words(["how", "are", "you"])
        o1 = Wordclip.objects.get(name="how")
        o2 = Wordclip.objects.get(name="are")
        o3 = Wordclip.objects.get(name="you")
        self.assertEqual(err, 0)
        self.assertEqual(lst, [o1, o2, o3])

    def test_not_found_in_db(self):
        """
        Test objects not being found in the database,
        the first word that can not be found will be returned
        """
        err, lst = self.ventriloquy.check_words(["how", "shooot"])
        self.assertEqual(err, -1)
        self.assertEqual(lst, "shooot")



    def test_creating_audio_success(self):
        """
        Test audio being successfully created
        """
        err, lst = self.ventriloquy.create_audio(["how", "are", "you", "people"])
        self.assertEqual(err, 0)
        self.assertEqual(lst, [])

    def test_creating_audio_failed(self):
        """
        Test audio created failed
        """
        err, lst = self.ventriloquy.create_audio(["how", "are", "you", "people", "damn", "it"])
        self.assertEqual(err, -1)
        self.assertEqual(lst, "damn")
