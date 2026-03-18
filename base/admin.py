from django.contrib import admin
from .models import * 
# Register your models here.
admin.site.register(Scholar)
admin.site.register(Performance)
admin.site.register(Follow)
admin.site.register(Semester)
admin.site.register(Subject)
admin.site.register(Question)
admin.site.register(Answer)
admin.site.register(QuestionPage)