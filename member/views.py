from django.shortcuts import render, redirect 
from django.http import HttpResponse
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from teacher.models import Subject, Teacher, ClassMember, AttendanceHistory
from django.db.models import Q
import numpy as np
from .models import *
from django.contrib import messages #import messages
import os
import cv2_ext
import face_recognition
import cv2
from django.core.files.storage import FileSystemStorage
from django.core.paginator import Paginator
import os

def uploadForTrain(request):
    if request.method == 'POST':

        try:
            profile = Profile.objects.get(user=request.user)
        except:
            profile = Profile.objects.create(user=request.user)

        folder_name = f'{request.user.username}'
        folder_path = "media/dataset/"+folder_name
        # create the folder if it doesn't exist
        if not os.path.exists(folder_path):
            os.makedirs(folder_path)

        files = request.FILES.getlist('file')

        fs = FileSystemStorage(location=folder_path)

        face_encodes = list()
        for f in files:
            if (str((f.name)).lower()).endswith((".png", ".jpg", ".jpeg")):

                filename = fs.save(f.name, f)

                imagePath = 'media/dataset/' + folder_name + '/' + filename
                name = request.user.first_name + '_' + request.user.last_name + ":" + request.user.username # khajornsak_krongyud: username
                # load the input image and convert it from BGR (OpenCV ordering)
                # to dlib ordering (RGB)
                image = cv2_ext.imread(imagePath)
                rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
                #Use Face_recognition to locate faces
                boxes = face_recognition.face_locations(rgb,model='hog')
                # compute the facial embedding for the face
                encoding = face_recognition.face_encodings(rgb, boxes)
                if len(encoding) > 1:
                    messages.error(request, f'ตรวจพบว่ามีมากกว่า 1 ใบหน้าใน 1 รูป ในรูป {f.name}')
                    os.remove(imagePath)
                    return redirect('/')
                elif len(encoding) == 0:
                    messages.error(request, f'ตรวจไม่พบใบหน้ารูป {f.name}')
                    os.remove(imagePath)
                    return redirect('/')
            
                if len(face_encodes) != 0:
                    result = face_recognition.compare_faces(face_encodes, encoding[0])
                    if result[0]:
                        encodeSave = Encode(face_name=name, user=request.user)
                        encodeSave.set_data(encoding[0])
                        encodeSave.save()

                        #เพิ่ม face_encode ไปยังลิสต์ 
                        face_encodes.append(encoding[0])
                    else:
                        messages.error(request, f'ตรวจพบว่าใบหน้ารูปนี้ {f.name} ไม่ตรงกับรูปที่แล้ว') 
                        return redirect('/')
                else:
                    encodeSave = Encode(face_name=name, user=request.user)
                    encodeSave.set_data(encoding[0])
                    encodeSave.save()

                    #เพิ่ม face_encode ไปยังลิสต์ 
                    face_encodes.append(encoding[0])
            else:
                messages.error(request, f'ตรวจพบว่าไฟล์ {f.name} ไม่ใช่นามสกุลไฟล์ .jpg หรือ .png')
                return redirect('/')
        
        profile.folder_image = "media/dataset/"+folder_name
        profile.save()
        
        messages.success(request, f'บันทึกเสร็จสิ้น')
        return redirect('/')

# Create your views here.
def Login(request):
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']

        user = authenticate(username=username, password=password)
        if user is not None and not user.is_superuser and not user.is_staff:
            login(request, user)
            return redirect('/')
        else:
            messages.error(request, 'ไม่พบผู้ใฃ้งาน')
            return redirect('login')
    else:
        return render(request, 'member/index.html')
def register(request):
    if request.method == "POST":
        username = request.POST['username']
        firstname = request.POST['firstname']
        lastname = request.POST['lastname']
        email = request.POST['email']
        password = request.POST['password']
        image = request.FILES['imgfile']
        if str((image.name)[-3:]) in ['jpg', 'png']:
            try:
                user = User.objects.create_user(username=username, email=email, password=password, first_name=firstname, last_name=lastname)
                profile = Profile(user=user, image=image)
                profile.save()
            except:
                messages.error(request, 'Username หรือ อีเมล อาจซ้ำ')
                return redirect('/register')
                
            return redirect('/')
    else:
        return render(request, 'member/register.html')
    
def Logout(request):
    logout(request)
    messages.success(request, "ออกจากระบบสำเร็จ")
    return redirect('/')

def course_reg(request):
    try:
        if request.user.profile.approved:
            return render(request, 'member/course_reg.html')
        else:
            return HttpResponse('<h1 style="text-align:center;">กรุณารอแอดมินอนุมัติสิทธิ</h1>')
    except:
        return HttpResponse('<h1 style="text-align:center;">กรุณารอแอดมินอนุมัติสิทธิ</h1>')

def registerCourse(request, id):
    subject = Subject.objects.get(id=id)
    profile = Profile.objects.get(user=request.user)
    if profile.folder_image:
        class_member = ClassMember(subject=subject, user=request.user)
        class_member.save()
        messages.success(request, 'ลงทะเบียนเสร็จสิ้น')
    else:
        messages.error(request, 'กรุณาอัพโหลดรูปภาพสำหรับจดจำใบหน้าก่อน')
    return redirect('course_reg')

def update_detail_profile(request):
    if request.method == "POST":
        firstname = request.POST['firstname']
        lastname = request.POST['lastname']
        addr = request.POST['address']
        phone = request.POST['phone']
        try:
            obj = Profile.objects.get(user=request.user)
            user = request.user
            try:
                user.first_name = firstname
                user.last_name = lastname
                user.save()
            except:
                messages.error(request, 'กรุณาตรวจสอบชื่อและนามสกุลของคุณ')
                redirect('/')

            obj.address = addr
            obj.phone_no = phone
            obj.save()
           
        except:
            obj = Profile.objects.create(user=request.user,
            address=addr, phone_no=phone,
            )
        messages.success(request, "บันทึกการเปลี่ยนแปลงเสร็จสิ้น")
        return redirect('/')

def update_image_profile(request):
    if request.method == "POST":
        image = request.FILES['imgfile']
        if str((image.name)[-3:]) in ['jpg', 'png']:
            
            try:
                obj = Profile.objects.get(user=request.user)
                obj.image = image
                obj.save()
                return redirect('/')
            except:
                obj = Profile.objects.create(user=request.user,
                    image=image
                )
                return redirect('/')
            
            #array to string
        else:
            messages.error('กรุณาอัพโหลดรูปนามสกุลไฟล์ png jpg jfif')
            return redirect('/')

def searchCourse(request):
    Allsubjects = list()
    search_subject = request.GET.get('subject_search')
    subjects = Subject.objects.filter(Q(SubjectCode__icontains=search_subject) | Q(SubjectName__icontains=search_subject)).select_related('Teacher')

    if subjects.exists():
            for sub in subjects:
                subject = dict()
                classMember = ClassMember.objects.filter(subject=sub, user=request.user)
                subject['SubjectCode'] = sub.SubjectCode
                subject['id'] = sub.id
                subject['SubjectName'] = sub.SubjectName
                subject['TeacherName'] = sub.Teacher.firstname + " " + sub.Teacher.lastname
                subject['statusReg'] = True if len(classMember) != 0 else False
                Allsubjects.append(subject)
            return render(request, 'member/course_reg.html', {'subjects': Allsubjects})
    else:
        messages.error(request, 'ไม่พบรายวิชา')
        return redirect('course_reg')

def historyEnroll(request, num_page):
    if request.user.profile.approved:
            history = AttendanceHistory.objects.filter(user=request.user)
            total_member = history.count()
            paginator = Paginator(history, per_page=10)
            historyOnPage = paginator.get_page(num_page)
            return render(request, 'member/history.html', {'history_enroll': historyOnPage})
    else:
            return HttpResponse('<h1 style="text-align:center;">กรุณารอแอดมินอนุมัติ</h1>')

    
    

