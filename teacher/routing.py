from django.urls import re_path
from . import consumers

websocket_urlpatterns = [
    re_path(r'^ws/roll-call/(?P<param>\w+)/$', consumers.FaceRecognitionConsumer.as_asgi()),#/ws/roll-call/sc246/
]