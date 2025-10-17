from django.db import models


class Support(models.Model):

    email = models.EmailField(null=True,blank=True)
    description = models.TextField(max_length=500, null=True,blank=True)
    file = models.FileField(upload_to='SupportFiles',null=True,blank=True)

    def __str__(self):
        return self.email