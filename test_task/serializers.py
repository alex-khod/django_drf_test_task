import json

from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator
from test_task import models as my_models
from test_task.validators import get_text_field_validators


class DefaultUserId:

    requires_context = True

    def __call__(self, serializer_field):
        user_id = serializer_field.context['user_id']
        return user_id


class PollResponseSerializer(serializers.ModelSerializer):

    user_id = serializers.HiddenField(default=DefaultUserId())
    text = serializers.JSONField()

    def to_internal_value(self, data):
        values = super().to_internal_value(data)
        return values

    def to_representation(self, data):
        repr_ = super().to_representation(data)
        return repr_

    def validate(self, data):
        type_ = data['question'].type
        answers = data['question'].get_answers
        responses = data['text']
        question = data["question"]

        validator_map = get_text_field_validators()
        for validator in validator_map[type_]:
            validator(responses, answers)

        # dirty check to not save 'inty' text like '1'
        if type_ in [
                my_models.PollQuestion.SINGLE_ANSWER,
                my_models.PollQuestion.MULTIPLE_ANSWERS]:
            data['text'] = list(map(int, data['text']))

        # dirty check to not deal with single quotes
        if type_ == my_models.PollQuestion.TEXT_ANSWER:
            data['text'] = json.dumps(data['text'])

        if question.poll.is_expired:
            raise serializers.ValidationError("Poll is expired")

        return data

    def create(self, data):
        instance = super().create(data)
        return instance

    class Meta:
        model = my_models.PollResponse
        # fields = "__all__"
        fields = ('question', 'user_id', 'text')


class PollQuestionSerializer(serializers.HyperlinkedModelSerializer):
    id = serializers.IntegerField(source='pk', read_only=True)
    responses = PollResponseSerializer(many=True, read_only=True)

    # extra fields for templates
    type_display = serializers.CharField(
        source='get_type_display', read_only=True)
    answers_display = serializers.JSONField(
        source='get_answers', read_only=True)

    class Meta:
        model = my_models.PollQuestion
        fields = "__all__"


class PollSerializer(serializers.HyperlinkedModelSerializer):
    id = serializers.IntegerField(source='pk', read_only=True)
    questions = PollQuestionSerializer(many=True, read_only=True)

    class Meta:
        model = my_models.Poll
        fields = "__all__"

    def validate_start_at(self, data):
        # note - validate <field> won't run
        # if that field is serialized through default value
        if self.instance is not None:
            raise serializers.ValidationError(
                'Changing poll start date is prohibited', code='gana')
        return data
