from django.core.management.base import BaseCommand
from test_task import models as my_models


def question_factory(poll):

    texts = ["What's up?", "What's hanging?", "What's wrong?"]
    types = [my_models.PollQuestion.SINGLE_ANSWER,
             my_models.PollQuestion.TEXT_ANSWER,
             my_models.PollQuestion.MULTIPLE_ANSWERS]
    answers = ["Sky,Space,ISS", "", "Weather,Mood,Boss"]

    questions = []
    for text, type_, answers in zip(texts, types, answers):
        question = my_models.PollQuestion.objects.create(
            poll=poll, text=text, type=type_, answers=answers)

        questions.append(question)
    return questions


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument(
            '--force', action="store_true", help='Force deleation and creation of Poll objects.')

    def handle(self, *args, **options):
        """Create basic data for polls."""

        exists = my_models.Poll.objects.exists()
        if exists:
            if options["force"]:
                my_models.Poll.objects.all().delete()
            else:
                print("There already are Poll objects in db."
                      " Pass --force arg to delete and create Polls again.")
                return None

        poll_titles = ["Poll 1", "Poll 2", "Poll 3"]

        polls = [my_models.Poll.objects.create(
            title=title) for title in poll_titles]

        for poll in polls:
            question_factory(poll)
