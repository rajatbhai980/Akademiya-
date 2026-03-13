from django.db import models
from django.contrib.auth import get_user_model
from django.contrib.auth.models import AbstractBaseUser

class Scholar(AbstractBaseUser):
    username = models.CharField(max_length=50)
    email = models.EmailField(unique=True, default='email')
    password = models.CharField(null=True, blank=True)
    photo = models.ImageField()
    semester = models.CharField(null=True, blank=True, max_length=20)
    bio = models.CharField(null=True, blank=True, max_length=100)
    subscribed = models.BooleanField(default=False)
    gems = models.IntegerField(default=0)

    def __str__(self): 
        return str(self.email)

class Follow(models.Model):
    follower = models.ForeignKey(Scholar, on_delete=models.CASCADE, related_name='follows')
    followee = models.ForeignKey(Scholar, on_delete=models.CASCADE, related_name='followed')

class Performance(models.Model): 
    user = models.OneToOneField(Scholar, on_delete=models.CASCADE, related_name='performance')
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
    


