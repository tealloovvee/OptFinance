from django.db import models

class News(models.Model):
    id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=200)
    content = models.TextField()
    published_at = models.DateTimeField()

    def __str__(self):
        return self.title
