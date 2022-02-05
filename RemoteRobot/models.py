from django.db import models


class Code(models.Model):
    code = models.TextField(default='')
    mac_address = models.CharField(max_length=20, unique=True)
    connection_type = models.CharField(max_length=10)