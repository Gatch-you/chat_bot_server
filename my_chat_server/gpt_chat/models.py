from django.db import models
from line_bot.models import User

# Create your models here.
class Thread(models.Model):
    thread_id = models.CharField(max_length=127, null=False, verbose_name='thread-id')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='thread_rerated')

    class Meta:
        db_table = "thread"
