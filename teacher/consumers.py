import json
from channels.generic.websocket import WebsocketConsumer
from teacher.models import *
from member.models import  Encode
from channels.layers import get_channel_layer
from adminsys.models import Camera
import os
import datetime
from asgiref.sync import async_to_sync
from .tasks import FaceRecognitionWebSocket

channel_layer = get_channel_layer()

class FaceRecognitionConsumer(WebsocketConsumer): # RollCallConsumer

    param = 'default'

    def connect(self):
        self.param = self.scope['url_route']['kwargs']['param']

        self.accept()

        async_to_sync(channel_layer.group_add)(
            self.param,
            self.channel_name
        )

    def disconnect(self, code="stop"):
        try:
            self.camera.update(statusCamera=False)

            async_to_sync(channel_layer.group_discard)(
                self.param,
                self.channel_name
            )

        except:
            pass

        self.close()
    
    def allmember(self, event):
        text = event['list_member']

        self.send(text_data=json.dumps({
            'type': 'allmember',
            'list_member' : text
        }))
    
    def camera_error(self, event):
        title = event['title']
        text = event['text']

        self.send(text_data=json.dumps({
            'type':'camera_error',
            'title' : title,
            'text' : text
            
        }))
        
    def send_rollcall(self, event):
        fullname = event['fullname']
        datetime = event['datetime']
        path = event['path']
        enrolled = event['enrolled']
        not_attend = event['not_attend']

        self.send(text_data=json.dumps({
            'type':'roll-call',
            'fullname': fullname,
            'datetime': datetime,
            'path': path,
            'enrolled' : enrolled,
            'not_attend' : not_attend,
        }))

    def receive(self, text_data):

        self.subject = Subject.objects.get(id = self.param)

        members = ClassMember.objects.filter(subject=self.subject)

        self.camera = Camera.objects.filter(id = (self.subject.SubjectRoom).id )

        date_now = datetime.datetime.now()
        date_now_string = date_now.strftime("%Y-%m-%d")

        subject_name_string = self.subject.SubjectName

        self.folder_name = f"media/history_roll_call/{date_now_string}/{subject_name_string}"

        if not os.path.exists(self.folder_name):
            os.makedirs(self.folder_name)

        self.camera.update(statusCamera=True)

        self.known_face_encodings = list()
        self.known_face_names = list()
        
        for member in members:
            know_face = Encode.objects.filter(user=member.user)
            for obj in know_face:
                self.known_face_encodings.append(list(obj.get_data()))
                self.known_face_names.append(obj.face_name)
        
        # ตัวแปรเริ่มต้น
        self.know_face_names_set = set(self.known_face_names)

        self.knowFaceNamesSetForSend = set()
        for text in self.know_face_names_set:
            self.knowFaceNamesSetForSend.add(text.split(":")[0])

        async_to_sync(channel_layer.group_send)(
            self.param,
            {
                'type': 'allmember',
                'list_member' : ','.join(self.knowFaceNamesSetForSend)
            }
        )

        user_time_hours, user_time_minutes = text_data.split(":")
        user_time_hours = int(user_time_hours)
        user_time_minutes = int(user_time_minutes)

        result = FaceRecognitionWebSocket.apply_async(args=(self.camera[0].Link, self.param,  user_time_hours, user_time_minutes, self.known_face_encodings, self.known_face_names, self.folder_name), task_id='unique_id')
        print(result)
    
        
        