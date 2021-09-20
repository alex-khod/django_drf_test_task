
import datetime

from django.contrib.auth.models import User
from django.core.management import call_command
from django.test import TestCase
from django.utils.timezone import now
from rest_framework.test import (APIClient, APIRequestFactory,
                                 force_authenticate)
from test_task import models as my_models
from test_task import views as my_views


class TestCommand(TestCase):

    def test_polls_created(self):
        assert(not my_models.Poll.objects.exists())
        call_command('populate')
        assert(my_models.Poll.objects.exists())

    def test_polls_not_created_again(self):
        call_command('populate')
        poll = my_models.Poll.objects.first()
        pk = poll.pk
        call_command('populate')
        poll = my_models.Poll.objects.first()
        assert(pk == poll.pk)

    def test_polls_created_again_when_forced(self):
        call_command('populate')
        poll = my_models.Poll.objects.first()
        pk = poll.pk
        call_command('populate', '--force')
        poll = my_models.Poll.objects.first()
        assert(pk < poll.pk)


class TestAuthentication(TestCase):
    def setUp(self):
        self.url = '/api/polls/'
        self.client = APIClient()

    def test_unauthenticated_fails(self):
        response = self.client.post(
            self.url, {'title': "sample text"})
        assert response.status_code == 401


class TestPollCRUD(TestCase):

    def setUp(self):
        call_command('populate')
        self.client = APIClient()
        user = User.objects.create(username='test', password='123')
        user.save()
        self.client.force_authenticate(user=user)

    def test_poll_update_succeeds(self):
        poll = my_models.Poll.objects.create(title='title')
        poll.save()

        new_title = 'sample_text'
        response = self.client.put(
            f'/api/polls/{poll.pk}/', {'title': new_title}, format='json')

        poll_ = my_models.Poll.objects.get(pk=poll.pk)

        assert poll_.title == new_title
        assert response.status_code == 200

    def test_poll_update_start_at_fails(self):
        poll = my_models.Poll.objects.create(title='title')
        poll.save()

        new_date = now()

        response = self.client.put(
            f'/api/polls/{poll.pk}/', {'start_at': new_date}, format='json')

        assert response.status_code == 400


class TestPollResponseValidation(TestCase):

    def setUp(self):
        call_command('populate')
        self.poll = my_models.Poll.objects.first()
        self.response_url = '/api/responses/'
        self.client = APIClient()

    def test_single_answer_ok(self):
        question = my_models.PollQuestion.objects.filter(
            type=my_models.PollQuestion.SINGLE_ANSWER).first()

        response = self.client.post(
            self.response_url, {'question': question.pk, 'text': [0]}, format='json')

        assert response.status_code == 201

    def test_multiple_answer_ok(self):
        question = my_models.PollQuestion.objects.filter(
            type=my_models.PollQuestion.MULTIPLE_ANSWERS).first()

        response = self.client.post(
            self.response_url, {'question': question.pk, 'text': [0, 1]}, format='json')

        assert response.status_code == 201

    def test_text_answer_ok(self):
        question = my_models.PollQuestion.objects.filter(
            type=my_models.PollQuestion.TEXT_ANSWER).first()

        response = self.client.post(
            self.response_url, {'question': question.pk, 'text': ['sample text']}, format='json')

        assert response.status_code == 201

    def test_empty_answer_fails(self):

        response = self.client.post(
            self.response_url, {}, format='json')

        assert response.status_code == 400

    def test_expired_poll_answer_fails(self):
        question = my_models.PollQuestion.objects.filter(
            type=my_models.PollQuestion.SINGLE_ANSWER).first()
        question.poll.expire_at = now() + datetime.timedelta(hours=-1)
        question.poll.save()

        response = self.client.post(
            self.response_url, {'question': question.pk, 'text': [0]}, format='json')

        assert response.status_code == 400

    def test_indistinct_answer_fails(self):
        question = my_models.PollQuestion.objects.filter(
            type=my_models.PollQuestion.MULTIPLE_ANSWERS).first()

        response = self.client.post(
            self.response_url, {'question': question.pk, 'text': [0, 0]}, format='json')

        assert response.status_code == 400

    def test_non_numeric_answer_fails(self):
        question = my_models.PollQuestion.objects.filter(
            type=my_models.PollQuestion.MULTIPLE_ANSWERS).first()

        response = self.client.post(
            self.response_url, {'question': question.pk, 'text': [[0], 0]}, format='json')

        assert response.status_code == 400

    def test_too_many_answers_fails(self):
        question = my_models.PollQuestion.objects.filter(
            type=my_models.PollQuestion.MULTIPLE_ANSWERS).first()

        n = len(question.get_answers)
        response = self.client.post(
            self.response_url, {'question': question.pk, 'text': list(range(n + 1))}, format='json')

        assert response.status_code == 400

    def test_big_answer_request_fails(self):
        question = my_models.PollQuestion.objects.filter(
            type=my_models.PollQuestion.MULTIPLE_ANSWERS).first()

        n = len(question.get_answers)
        response = self.client.post(
            self.response_url, {'question': question.pk, 'text': [n]}, format='json')

        assert response.status_code == 400
