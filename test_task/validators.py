from rest_framework.serializers import ValidationError
from test_task import models as my_models


def validate_single_len(responses, answers):
    if len(responses) > 1:
        raise ValidationError(
            'Multiple responses for single-answer question', code='spoof')


def validate_non_empty(responses, answers):
    if len(responses) == 0:
        raise ValidationError(
            'Empty response sent', code='spoof')


def validate_non_empty(responses, answers):
    if len(responses) == 0:
        raise ValidationError(
            'Empty response sent', code='empty')


def validate_non_empty_text(responses, answers):
    if responses[0] == '':
        raise ValidationError(
            'Empty response sent', code='empty')


def validate_is_numeric(responses, answers):
    try:
        responses = list(map(int, responses))
    except (ValueError, TypeError):
        raise ValidationError(
            'Response must be list of numbers', code='spoof')


def validate_is_text(responses, answers):
    if type(responses[0]) != str:
        raise ValidationError('Non-textual response for text answer')


def validate_max_value(responses, answers):
    responses = list(map(int, responses))

    def answer_id_less_response_id(x):
        if x >= len(answers):
            raise ValidationError(
                'The response value is bigger than valid answer quantity', code='spoof')
    list(map(answer_id_less_response_id, responses))


def validate_max_len(responses, answers):
    if len(responses) > len(answers):
        raise ValidationError(
            'Too many responses for multiple-answer question')


def validate_distinct(responses, answers):
    if (len(responses) != len(set(responses))):
        raise ValidationError(
            'Response values must be distinct', code='spoof')


def get_text_field_validators():
    validator_map = {
    }

    validator_map[my_models.PollQuestion.SINGLE_ANSWER] = [
        validate_single_len,
        validate_is_numeric,
        validate_max_value,
        validate_non_empty
    ]

    validator_map[my_models.PollQuestion.TEXT_ANSWER] = [
        validate_single_len,
        validate_is_text,
        validate_non_empty_text
    ]

    validator_map[my_models.PollQuestion.MULTIPLE_ANSWERS] = [
        validate_non_empty,
        validate_max_len,
        validate_is_numeric,
        validate_distinct,
        validate_max_value,
    ]
    return validator_map
