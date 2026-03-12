from django.db import models
from django.contrib.auth import get_user_model
User = get_user_model()

# Create your models here.
class Profile(models.Model): 
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    photo = models.ImageField()
    semester = models.CharField(null=True, blank=True, max_length=20)
    bio = models.CharField(null=True, blank=True, max_length=100)
    subscribed = models.BooleanField(default=False)
    follows = models.ManyToManyField(User, related_name='follower')
    gems = models.IntegerField(default=0)


class Performance(models.Model): 
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='performance')
    level = models.IntegerField(default=1)
    experience = models.IntegerField(default=0)
    solved = models.IntegerField(default=0)
    correct = models.IntegerField(default=0)
    wrong = models.IntegerField(default=0)
    correct_ratio = models.DecimalField(default=0, decimal_places=3, max_digits=3)

class Semester(models.Model): 
    name = models.CharField(max_length=40)

class Subject(models.Model):
    name= models.CharField(max_length=40)
    semester = models.ForeignKey(Semester, on_delete=models.CASCADE, related_name='subjects')

class Question(models.Model): 
    description = models.CharField(max_length=30)
    subject = models.ForeignKey(Semester, on_delete=models.CASCADE, related_name='questions')
    hint = models.CharField(max_length=40)
    full_explaination = models.CharField(max_length=100)

class Answer(models.Model): 
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='answers')
    description = models.CharField(max_length=40)
    coorect = models.BooleanField()
    


