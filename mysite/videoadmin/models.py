from django.db import models

# Create your models here.
class CeleryTask(models.Model):
    celery_task_id = models.CharField(max_length = 50, unique=True)
    celery_task_status = models.CharField(max_length = 20, default=None)


    def __unicode__(self):
        return self.celery_task_id


    def __str__(self):
        return '%s' % (self.celery_task_id)
