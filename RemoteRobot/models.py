from django.db import models


class Code(models.Model):
    code = models.TextField(default='')
    password = models.CharField(max_length=20, unique=True)
