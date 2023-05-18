from __future__ import absolute_import, unicode_literals
from celery import shared_task
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from teacher.models import *
from django.contrib.auth.models import User
from adminsys.models import Camera
import face_recognition
import cv2
import numpy as np
import cv2_ext
from PIL import ImageFont, Image, ImageDraw
import pytz
from datetime import datetime
import asyncio

channel_layer = get_channel_layer()
tz = pytz.timezone('Asia/Bangkok')

@shared_task
def FaceRecognitionWebSocket(camera, subjectID, user_time_hours, user_time_minutes, known_face_encodings, known_face_names, folder_name):
    if camera == "0":
        video_capture = cv2.VideoCapture(0)
    else:
        video_capture = cv2.VideoCapture(camera)
    
    
    subject = Subject.objects.get(id = subjectID)

    roll_call = set()
    know_face_names_set = set(known_face_names)

    face_locations = []
    face_encodings = []
    face_names = []
    process_this_frame = True

    font_path = 'ANGSA.ttf'
    font = ImageFont.truetype(font_path, 32)
    

    while True:

        now = datetime.now(tz)
        current_time_hours = int(now.strftime("%H"))
        current_time_minutes = int(now.strftime("%M"))

        if (current_time_hours > user_time_hours):
            loop = asyncio.get_event_loop()
            loop.run_until_complete(sendDisconnect(subjectID))
            break

        elif (user_time_hours == current_time_hours) and (current_time_minutes > user_time_minutes):
            loop = asyncio.get_event_loop()
            loop.run_until_complete(sendDisconnect(subjectID))
            break

        # Grab a single frame of video
        ret, frame = video_capture.read()
        if frame is None:

            loop = asyncio.get_event_loop()
            loop.run_until_complete(sendCameraError(subjectID))# ไม่สามารถใช้งานกล้องได้
            break

        # Only process every other frame of video to save time
        if process_this_frame:
            # Resize frame of video to 1/4 size for faster face recognition processing
            small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)

            # Convert the image from BGR color (which OpenCV uses) to RGB color (which face_recognition uses)
            rgb_small_frame = small_frame[:, :, ::-1]
            
            # Find all the faces and face encodings in the current frame of video
            face_locations = face_recognition.face_locations(rgb_small_frame)
            face_encodings = face_recognition.face_encodings(rgb_small_frame, face_locations)

            face_names = []
            for face_encoding in face_encodings:
                # See if the face is a match for the known face(s)
                matches = face_recognition.compare_faces(known_face_encodings, face_encoding)
                name = "Unknown"

                # # If a match was found in known_face_encodings, just use the first one.
                # if True in matches:
                #     first_match_index = matches.index(True)
                #     name = known_face_names[first_match_index]

                # Or instead, use the known face with the smallest distance to the new face
                face_distances = face_recognition.face_distance(known_face_encodings, face_encoding)
                best_match_index = np.argmin(face_distances)
                if matches[best_match_index]:
                    name = known_face_names[best_match_index]
                    current_time = datetime.now(tz)

                face_names.append(name)

        process_this_frame = not process_this_frame

        for (top, right, bottom, left), name in zip(face_locations, face_names):
            # Scale back up face locations since the frame we detected in was scaled to 1/4 size
            top *= 4
            right *= 4
            bottom *= 4
            left *= 4

            cv2.rectangle(frame, (left, top), (right, bottom), (0, 0, 255), 2)
            
            img_pil = Image.fromarray(frame)
            draw = ImageDraw.Draw(img_pil)
            draw.text((left + 6, bottom - 6),  name.split(":")[0] , font = font, fill = ((255, 255, 255, 0)))
            frame = np.array(img_pil)
        if len(face_names) != 0 and face_names[0] != "Unknown":
            if len(face_names) > 1:# ถ้ามีใบหน้าหลายคนเข้ามาพร้อมกัน
                for name_for in face_names:
                    if name_for not in roll_call:
                            print(face_names)
                            roll_call.add(name_for)
                            name_for_save, name_for_use = name_for.split(":")
                            path_roll_call = f"{folder_name}/{name_for_save}.png"
                            
                            cv2_ext.imwrite(path_roll_call, frame)

                            firstname, lastname = name_for_save.split("_")
                            user = User.objects.get(username=name_for_use)
                            camera_query = Camera.objects.get(id = (subject.SubjectRoom).id)

                            attenHis = AttendanceHistory(user=user, subject=subject, camera=camera_query, date=current_time.strftime("%Y-%m-%d"), time=current_time.strftime("%H:%M:%S"), image=path_roll_call)
                            attenHis.save()

                            date_for_send = str(current_time.strftime("%H:%M:%S"))

                            not_attend = len(know_face_names_set) - len(roll_call)
                            enrolled = len(roll_call)
                            fullname = firstname + " " + lastname

                            loop = asyncio.get_event_loop()
                            loop.run_until_complete(sendDataEnroll(subjectID, fullname, date_for_send, path_roll_call, enrolled, not_attend))


            else:
                if face_names[0] not in roll_call:
                    print(face_names)
                    roll_call.add(face_names[0])
                    name_for_save, name_for_use = face_names[0].split(":")
                    path_roll_call = f"{folder_name}/{name_for_save}.png"
                    cv2_ext.imwrite(path_roll_call, frame)

                    firstname, lastname = name_for_save.split("_")
                    user = User.objects.get(username=name_for_use)
                    camera_query = Camera.objects.get(id = (subject.SubjectRoom).id)

                    attenHis = AttendanceHistory(user=user, subject=subject, camera=camera_query, date=current_time.strftime("%Y-%m-%d"), time=current_time.strftime("%H:%M:%S"), image=path_roll_call)
                    attenHis.save()

                    date_for_send = str(current_time.strftime("%H:%M:%S"))

                    not_attend = len(know_face_names_set) - len(roll_call)
                    enrolled = len(roll_call)
                    fullname = firstname + " " + lastname

                    loop = asyncio.get_event_loop()
                    loop.run_until_complete(sendDataEnroll(subjectID, fullname, date_for_send, path_roll_call, enrolled, not_attend))

        if len(roll_call) == len(know_face_names_set):
            loop = asyncio.get_event_loop()
            loop.run_until_complete(sendDisconnect(subjectID))
            break

    # Release handle to the webcam
    video_capture.release()
    cv2.destroyAllWindows()

async def sendDataEnroll(subjectID, fullname, datetime, path, enrolled, not_attend):
    await channel_layer.group_send(
            subjectID,
            {
                'type':'send.rollcall',
                'fullname': fullname,
                'datetime': datetime,
                'path': "/" + path,
                'enrolled' : enrolled,
                'not_attend' : not_attend,
            }
        )

async def sendDisconnect(subjectID):
    await channel_layer.group_send(
        subjectID,
                {
                    'type': 'disconnect',
                }
        )

async def sendCameraError(subjectID):
    await channel_layer.group_send(
                subjectID,
                {
                        'type': 'camera_error',
                        'title' : 'กล้องเกิดข้อผิดพลาด กรุณาตรวจสอบอินเทอร์เน็ต',
                        'text' : 'กรุณาตรวจสอบกล้องของห้อง หรือ ตรวจสอบอินเทอร์เน็ตของคุณ'
                }
            )