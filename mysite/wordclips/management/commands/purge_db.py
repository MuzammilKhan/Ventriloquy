from django.core.management.base import BaseCommand
from wordclips.models import Speaker, Wordclip
import wordclips
import os

class Command(BaseCommand):
    args = '<no argument needed ...>'
    help = 'MORE CAREFUL! This command will delete all the data in the database'
    APP_ROOT = os.path.abspath(os.path.dirname(wordclips.__file__))

    def handle(self, *args, **options):
        # Deleting all the objects in the table
        Wordclip.objects.all().delete()
        Speaker.objects.all().delete()
