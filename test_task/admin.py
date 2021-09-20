from django.contrib import admin
from test_task import models

# Register your models here.


class PollAdmin(admin.ModelAdmin):
    pass


class PollQuestionAdmin(admin.ModelAdmin):
    pass


admin.site.register(models.Poll, PollAdmin)
admin.site.register(models.PollQuestion, PollQuestionAdmin)
admin.site.register(models.PollResponse, PollQuestionAdmin)
