import datetime

from django.contrib.contenttypes.fields import (GenericForeignKey,
                                                GenericRelation)
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.utils.timezone import now

ModelClass = models.Model


def seconds_ago():
    return now() + datetime.timedelta(seconds=-5)


def duration_week():
    return now() + datetime.timedelta(days=7)


class Poll(ModelClass):
    """
        Collection of questions.
    """
    title = models.CharField(default="Untitled", max_length=255)
    # seconds ago fix flaky tests that check is_expired
    start_at = models.DateTimeField(default=seconds_ago)
    expire_at = models.DateTimeField(default=duration_week)
    description = models.CharField(default="I'm a Poll", max_length=255)

    @property
    def is_expired(self):
        is_expired = now() < self.start_at
        is_expired = is_expired or (now() > self.expire_at)
        return is_expired

    def __str__(self):
        desc = f"Poll: {self.pk} - {self.title}"
        return desc


class PollQuestion(ModelClass):
    poll = models.ForeignKey(
        Poll, related_name="questions", on_delete=models.CASCADE)
    text = models.CharField(default="What's up?", max_length=255)
    # Collects answers as comma-separated field
    answers = models.CharField(max_length=255)

    SINGLE_ANSWER = "SA"
    MULTIPLE_ANSWERS = "MA"
    TEXT_ANSWER = "TA"

    POLL_TYPE_CHOICES = (
        (SINGLE_ANSWER, "Single answer"),
        (MULTIPLE_ANSWERS, "Multiple answers"),
        (TEXT_ANSWER, "Text answer"),
    )

    type = models.CharField(
        choices=POLL_TYPE_CHOICES, default=SINGLE_ANSWER, max_length=255)

    def __str__(self):
        desc = f"PollQuestion: {self.pk} - {self.text}"
        return desc

    @property
    def get_answers(self):
        # Deseralized as JSON
        values = self.answers.split(',')
        return values


class PollResponse(ModelClass):

    text = models.CharField(max_length=255)
    # Didn't play well with unique_together
    # user_id = models.UUIDField()
    user_id = models.CharField(max_length=32)
    question = models.ForeignKey(
        PollQuestion, related_name="responses", on_delete=models.CASCADE)

    def __str__(self):
        desc = f"PollResponse: {self.pk} - {self.text} of {self.user_id}"
        return desc

    class Meta:
        unique_together = ('user_id', 'question')
