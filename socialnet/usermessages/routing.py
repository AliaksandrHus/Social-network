from django.urls import re_path, path
from . import consumers

websocket_urlpatterns = [
    # re_path(r'ws/messages/dialog-(?P<dialog_id>[^/]+)/$', consumers.ChatConsumer.as_asgi()),
    re_path(r'ws/messages/dialog-(?P<dialog_id>[^/]+)/$', consumers.ChatConsumer.as_asgi()),
]