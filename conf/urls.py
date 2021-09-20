"""test_task URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

import debug_toolbar
from django.contrib import admin
from django.contrib.staticfiles.views import serve as serve_static
from django.urls import include, path, re_path
from rest_framework import routers
from test_task import views

router = routers.DefaultRouter()
router.register(r'polls', views.APIPollViewSet, 'poll-api')
router.register(r'questions', views.APIPollQuestionViewSet, 'question-api')
router.register(r'responses', views.APIPollResponseViewSet)

dashboard_router = routers.DefaultRouter()
dashboard_router.register(r'polls', views.PollViewSet, 'poll')
dashboard_router.register(r'questions', views.PollQuestionViewSet)

urlpatterns = [
    path('api/', include(router.urls)),
    path('api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    path('dashboard/', include(dashboard_router.urls)),
    path('admin/', admin.site.urls),
    path('', views.react),
    path('__debug__/', include(debug_toolbar.urls)),
    re_path(r'^static/(?P<path>.*)$', serve_static)
]
