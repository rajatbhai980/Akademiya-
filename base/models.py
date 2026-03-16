from django.db import models
from django.contrib.auth import get_user_model
from django.contrib.auth.models import AbstractBaseUser, UserManager, PermissionsMixin
from django.apps import apps
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db.models.signals import post_save
from django.dispatch import receiver

class ScholarManager(UserManager): 
    def create_superuser(self, email=None, password=None):
        email = self.normalize_email(email)

        user = self.model(email=email)
        user.is_superuser=True
        user.is_staff=True
        user.set_password(password)
        user.save(using=self._db)

        return user 

class Scholar(AbstractBaseUser, PermissionsMixin):
    username = models.CharField(max_length=50, null=True, blank=True)
    email = models.EmailField(unique=True, default='email')
    password = models.CharField(null=True, blank=True)
    photo = models.ImageField(null=True, blank=True)
    semester = models.IntegerField(null=True, blank=True, validators=[MinValueValidator(1), MaxValueValidator(8)])
    bio = models.CharField(null=True, blank=True, max_length=100)
    subscribed = models.BooleanField(default=False)
    gems = models.IntegerField(default=0)
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)


    objects = ScholarManager()
    USERNAME_FIELD = 'email'

    def __str__(self): 
        return str(self.email)

class Follow(models.Model):
    follower = models.ForeignKey(Scholar, on_delete=models.CASCADE, related_name='follows')
    followee = models.ForeignKey(Scholar, on_delete=models.CASCADE, related_name='followed')

@receiver(post_save, sender=Scholar)
def create_performance(sender, instance, created, **kwargs): 
    if created: 
        Performance.objects.create(user=instance)

class Performance(models.Model): 
    user = models.OneToOneField(Scholar, on_delete=models.CASCADE, related_name='performance')
    level = models.IntegerField(default=1)
    experience = models.IntegerField(default=0)
    attempted = models.IntegerField(default=0)
    correct = models.IntegerField(default=0)
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
    


