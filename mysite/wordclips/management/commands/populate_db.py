from django.core.management.base import BaseCommand
from wordclips.models import Speaker, Wordclip
import wordclips
import os

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
        CLIPS_DIR = os.path.abspath(self.APP_ROOT + "/clips")
        # print('clips path: ' + CLIPS_DIR)
        spk_first_name = "Barack"
        spk_last_name = "Obama"
        spk = Speaker(first_name=spk_first_name, last_name=spk_last_name)
        spk.save()
        for p in os.listdir(CLIPS_DIR):
            if os.path.isdir(os.path.abspath(CLIPS_DIR + '/' +p)):
                # Create clips in database
                w = Wordclip(name=p, soundpath=os.path.abspath(CLIPS_DIR + '/' + p))
                w.save()
                w.speaker.add(spk)