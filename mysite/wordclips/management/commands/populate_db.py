from django.core.management.base import BaseCommand
from wordclips.models import Speaker, Wordclip
import wordclips
import os

from django.conf import settings

'''
    Command to populate database with path of wordclips
'''
class Command(BaseCommand):
    args = '<no argument needed ...>'
    help = 'CAREFUL! Populating data into the database'
    APP_ROOT = os.path.abspath(os.path.dirname(wordclips.__file__))


    '''
        Populating database with the clips in the folder
    '''
    def handle(self, *args, **options):
        # Assuming the clips folder is under the app folder
        # print('app_path: ' + self.APP_ROOT)


        # print('clips path: ' + CLIPS_DIR)
        spk_first_name = "barack"
        spk_last_name = "obama"
        CLIPS_DIR = settings.SITE_ROOT + '/../media/clips/' + spk_last_name + '/'
        print(CLIPS_DIR)
        spk = Speaker(firstname=spk_first_name, lastname=spk_last_name)
        spk.save()
        for p in os.listdir(CLIPS_DIR):
            if os.path.isdir(os.path.abspath(CLIPS_DIR + p)):
                # Create clips in database
                w = Wordclip(name=p, soundpath=os.path.abspath(CLIPS_DIR + p))
                w.save()
                w.speaker = spk
                w.save()

        spk_first_name = "donald"
        spk_last_name = "trump"
        CLIPS_DIR = settings.SITE_ROOT + '/../media/clips/' + spk_last_name + '/'
        print(CLIPS_DIR)
        spk = Speaker(firstname=spk_first_name, lastname=spk_last_name)
        spk.save()
        for p in os.listdir(CLIPS_DIR):
            if os.path.isdir(os.path.abspath(CLIPS_DIR + p)):
                # Create clips in database
                w = Wordclip(name=p, soundpath=os.path.abspath(CLIPS_DIR + p))
                w.save()
                w.speaker = spk
                w.save()
