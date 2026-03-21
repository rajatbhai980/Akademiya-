from django.db import models
from django.contrib.auth import get_user_model
from django.contrib.auth.models import AbstractBaseUser, UserManager, PermissionsMixin
from django.apps import apps
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db.models.signals import post_save
from django.dispatch import receiver
from datetime import date

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
    @property
    def correct_ratio(self): 
        if self.attempted != 0: 
            cr = (self.correct / self.attempted) * 100 
            return cr       
        return 0 

class GameSession(models.Model):
    user = models.OneToOneField(Scholar, null=True, blank=True, on_delete=models.CASCADE)
    mode = models.CharField(max_length=50)
    current_index = models.IntegerField(default=0)
    status = models.CharField(max_length=20, default="in_progress")
    last_activity = models.DateTimeField(auto_now=True)

class QuizPlan(models.Model): 
    game_session = models.OneToOneField(GameSession, on_delete=models.CASCADE)

class Semester(models.Model): 
    name = models.CharField(max_length=40)

class Subject(models.Model):
    name = models.CharField(max_length=40)
    semester = models.ForeignKey(Semester, on_delete=models.CASCADE, related_name='subjects', null=True)

class QuestionPage(models.Model): 
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name='pages', null=True, blank=True)
    year = models.DateField(default=date.today)
    quiz_plans = models.ManyToManyField(QuizPlan, related_name='pages')

class PlayerChoices(models.Model): 
    game_session = models.ForeignKey(GameSession, on_delete=models.CASCADE, related_name='player_choices')
    page = models.OneToOneField(QuestionPage, on_delete=models.CASCADE)

class Question(models.Model): 
    description = models.CharField(max_length=200)
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name='questions', null=True)
    page = models.ForeignKey(QuestionPage, on_delete=models.CASCADE, related_name='questions', null=True)
    hint = models.CharField(max_length=200, null=True)
    full_explaination = models.CharField(max_length=400, null=True)
    player_choices = models.ForeignKey(PlayerChoices, on_delete=models.SET_NULL, null=True, blank=True, related_name='questions')

class Answer(models.Model): 
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='answers', null=True)
    description = models.CharField(max_length=40)
    correct = models.BooleanField(default=False)
    player_choices = models.ForeignKey(PlayerChoices, on_delete=models.SET_NULL, null=True, blank=True, related_name='answers')





    


