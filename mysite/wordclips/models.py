from django.db import models



class Speaker(models.Model):
    """
        Representing the speaker of a word
    """
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)

    def __unicode__(self):
        return self.first_name + ' ' + self.last_name


    def __str__(self):
        return '%s %s' % (self.first_name, self.last_name)


class Wordclip(models.Model):
    """
    The wordclip object contains the word itself, the speaker of
    the word and the path to its soundtrack
    """
    name = models.CharField(max_length=100)
    # one word can be spoken by many speakers and vice versa
    speaker = models.ForeignKey(Speaker, null=True)
    soundpath = models.CharField(max_length=200)

    def __unicode__(self):
        return self.name

    def __str__(self):
        return self.name
