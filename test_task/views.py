import uuid

from django.db import models
from django.shortcuts import render
from rest_framework import (decorators, filters, generics, pagination,
                            permissions, renderers, viewsets)
from rest_framework.response import Response
from test_task import models as my_models
from test_task import serializers as my_serializers

# Create your views here.


class SmallPagination(pagination.PageNumberPagination):
    page_size = 2
    page_size_query_param = 'page_size'
    max_page_size = 5


class UserOwnerFilterBackend(filters.BaseFilterBackend):
    def filter_queryset(self, request, queryset, view):
        user_id = request.session['user_id']
        return queryset.filter(questions__responses__user_id=user_id)


class JSONRendererMixin:
    def get_renderers(self):
        return [renderers.JSONRenderer()]


class PollViewSet(viewsets.ModelViewSet):
    renderer_classes = [renderers.BrowsableAPIRenderer, renderers.JSONRenderer]
    serializer_class = my_serializers.PollSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        user_id = self.request.session['user_id']
        queryset = my_models.Poll.objects.all().prefetch_related(models.Prefetch(
            'questions',
        ),
            models.Prefetch('questions__responses',
                            queryset=my_models.PollResponse.objects.filter(user_id=user_id))
        ).order_by('pk').distinct()  # Filtering returns duplicates for some reason
        return queryset

    @decorators.action(methods=['get'], detail=False)
    def me(self, request, pk=None):
        self.filter_backends = [UserOwnerFilterBackend]
        return self.list(request)


class APIPollViewSet(JSONRendererMixin, PollViewSet):
    pass


class PollQuestionViewSet(viewsets.ModelViewSet):
    queryset = my_models.PollQuestion.objects.all()
    serializer_class = my_serializers.PollQuestionSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]


class APIPollQuestionViewSet(JSONRendererMixin, PollQuestionViewSet):
    pass


class APIPollResponseViewSet(JSONRendererMixin, viewsets.ModelViewSet):
    queryset = my_models.PollResponse.objects.all()
    serializer_class = my_serializers.PollResponseSerializer

    def perform_create(self, data):
        pass
        super().perform_create(data)

    def get_serializer_context(self):
        context = super().get_serializer_context()
        # print(self.request.data)
        # print(self.request.session["user_id"])
        context.update({"user_id": self.request.session["user_id"]})
        return context


def react(request, *args, **kwargs):
    return render(request, 'frontend.html')
