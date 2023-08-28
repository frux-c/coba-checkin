from django.db import models
import random
from string import ascii_uppercase
from django.utils.text import slugify
import os


def generateSlug() -> str:
    TAG_QUERY = []
    if os.path.exists('tags.txt'):
        file = open('tags.txt','a+')
        TAG_QUERY = file.read().split('\n')
    else:
        file = open('tags.txt','w+')
    letters = [l for l in ascii_uppercase]
    new_tag = "".join(random.choices(letters,k=8))
    while new_tag in TAG_QUERY:
        print(new_tag)
        new_tag = "".join(random.choices(letters,k=8))
    file.write(new_tag+'\n')
    file.close()
    return new_tag

# Create your models here.
class Task(models.Model):
    name = models.CharField(max_length=100,verbose_name="Task")
    description = models.TextField(max_length=500)
    completed = models.BooleanField(default=False)

    def __str__(self):
        return self.name


class ServiceCase(models.Model):
    title = models.CharField(max_length=50,default="")
    url = models.CharField(max_length=500,default="")
    tasks = models.ManyToManyField(Task,blank=True)
    status = models.BooleanField(default=False,verbose_name="Status")
    slug = models.SlugField(unique=True,default="",editable=False)

    def save(self, *args, **kwargs):
        if self._state.adding:
            print('self is new')
            self.slug = slugify(generateSlug(),allow_unicode=True)
        print(self.slug)
        super().save(*args,**kwargs)

    def __str__(self):
        return self.title

