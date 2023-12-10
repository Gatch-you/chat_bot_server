from django.db import models

# Create your models here.
class User(models.Model):
    user_id = models.CharField(max_length=127, null=False, verbose_name="user-id")

    class Meta:
        db_table = "user"
