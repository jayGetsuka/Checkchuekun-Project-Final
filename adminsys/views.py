from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from .models import *
from member.models import Profile
from teacher.models import Teacher
from django.core.paginator import Paginator
import hashlib
from django.contrib import messages #import messages
import pandas as pd
from urllib.request import urlopen, urlretrieve
from django.core.files import File
import os
import shutil
from django.db.models import Q
from django.contrib.auth import authenticate, login, logout

# Create your views here.
def Login(request):
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None and user.is_superuser:
            login(request, user)
            request.session['count_user_unconfirm'] = Profile.objects.filter(approved=False).count()
            request.session['count_teacher'] = (Teacher.objects.all()).count()
            request.session['count_camera'] = (Camera.objects.all()).count()
            request.session['count_member'] = Profile.objects.filter(approved=True).count()
            return render(request, 'adminsys/index.html')

        else:
            # Return an 'invalid login' error message.

            messages.error(request, "กรุณาตรวจสอบ ชื่อผู้ใช้ หรือ รหัสผ่าน")
            return render(request, 'adminsys/index.html')
            
    else:
        #request GET
        request.session['count_user_unconfirm'] = Profile.objects.filter(approved=False).count()
        request.session['count_teacher'] = (Teacher.objects.all()).count()
        request.session['count_camera'] = (Camera.objects.all()).count()
        request.session['count_member'] = Profile.objects.filter(approved=True).count()
        return render(request, 'adminsys/index.html')

def Logout(request):
    logout(request)
    return redirect("/adminsys")

def confirmUser(request):
    user_unconfirm = Profile.objects.filter(approved=False)
    return render(request, 'adminsys/confirm_user.html', {'user_unconfirm': user_unconfirm})

def confirmToMember(request, id):
    try:
        profile = Profile.objects.get(user__id=id)
        if not profile.folder_image:
            messages.error(request, "ไม่สามารถยืนยันได้เนื่องจากผู้ใช้ไม่อัพโหลดรูปภาพสำหรับจดจำใบหน้า")
            return redirect("/adminsys/confirm_user")
        else:
            profile.approved = True
            profile.save()
            request.session['count_user_unconfirm'] -= 1
            messages.success(request, "บันทึกเป็นสมาชิกเสร็จสิ้น")
            return redirect('/adminsys/confirm_user')
    except:
        messages.error(request, "ไม่พบผู้ใช้งานไอดีนี้")
        return redirect('/adminsys/confirm_user')

def deleteUser(request, id):
    try:
        user = User.objects.get(id=id)
        path = "media/dataset/"+user.first_name+"_"+user.last_name
        if os.path.exists(path):
            shutil.rmtree(path, ignore_errors=True)
        user.delete()
        request.session['count_user_unconfirm'] -= 1
        messages.success(request, "ลบเสร็จสิ้น")
        return redirect('/adminsys/confirm_user')
    except:
        messages.error(request, "เกิดข้อผิดพลาดในการลบ")
        return redirect('/adminsys/confirm_user')
       
    
def ShowMember(request, num_page):
    profile = Profile.objects.filter(approved=True)
    query = request.GET.get('search')
    if query:
        profile = Profile.objects.filter(
            Q(user__username__icontains=query) |
            Q(user__first_name__icontains=query) | Q(user__last_name__icontains=query)
        ).distinct()
    total_member = profile.count()
    paginator = Paginator(profile, per_page=10)
    memberOnPage = paginator.get_page(num_page)
    return render(request, 'adminsys/showMember.html', {'all_member': memberOnPage, 'total_member': total_member})

def ShowTeacher(request, num_page):
    teachers = Teacher.objects.all().order_by("firstname")
    query = request.GET.get('search')
    if query:
        teachers = Teacher.objects.filter(
            Q(username__icontains=query) | Q(email__icontains=query) | Q(department__icontains=query) |
            Q(firstname__icontains=query) | Q(lastname__icontains=query)
        ).distinct()
    total_teacher = teachers.count()
    paginator = Paginator(teachers, per_page=10)
    teacherOnPage = paginator.get_page(num_page)
    return render(request, 'adminsys/showTeacher.html', {'all_teacher': teacherOnPage, 'total_teacher': total_teacher})

def ShowCamera(request, num_page):
    cameras = Camera.objects.all()
    query = request.GET.get('search')
    if query:
        cameras = Camera.objects.filter(
            Q(NumberRoom__icontains=query)
        ).distinct()
    total_camera = cameras.count()
    paginator = Paginator(cameras, per_page=10)
    cameraOnPage = paginator.get_page(num_page)
    return render(request, 'adminsys/showCamera.html', {'all_camera': cameraOnPage, 'total_camera': total_camera})

def addMember(request):
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']
        email = request.POST['email']
        fname = request.POST['fname']
        lname = request.POST['lname']
        image = request.FILES['profile']
        phone = request.POST.get('phone_no', None)
        addr = request.POST.get('address', None)

        if str((image.name)[-3:]) in ['jpg', 'png', 'fif']:
            try:
                user = User.objects.create_user(username=username, email=email, password=password, first_name=fname, last_name=lname)
                profile = Profile(user=user, image=image, phone_no=phone, address=addr, approved=True)
                profile.save()
                messages.success(request, "เพิ่มสมาชิกเสร็จสิ้น")
                return redirect('/adminsys/addMember')
                
            except:
                messages.error(request, "๊Username หรือ Email ซ้ำกัน")
                return redirect('/adminsys/addMember')
        else:
            messages.error(request, "กรุณาอัพโหลดไฟล์ .png .jpg .jfif")
            return redirect('/adminsys/addMember')
            
    else:
        return render(request, 'adminsys/addMember.html')

def addTeacher(request):
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']
        email = request.POST['email']
        fname = request.POST['fname']
        lname = request.POST['lname']
        phone = request.POST.get('phone_no', None)
        department = request.POST.get('department', None)
        hashPassword = hashlib.sha256(password.encode("utf-8")).hexdigest()
        try:
            teacher = Teacher(username=username, password=hashPassword, email=email, firstname=fname, lastname=lname, phone_no=phone, department=department)
            teacher.save()
            messages.success(request, "บันทึกอาจารย์เสร็จสิ้น")
            return redirect("/adminsys/addTeacher")
        except:
            messages.error(request, "เกิดข้อผิดพลาดในการเพิ่มอาจารย์")
            return redirect("/adminsys/addTeacher")
    else:
        return render(request, 'adminsys/addTeacher.html')

def addCamera(request):
    if request.method == "POST":
        room = request.POST['room']
        link = request.POST['link']

        try:
            camera = Camera(NumberRoom=room, Link=link)
            camera.save()
            messages.success(request, "เพิ่มกล้องเสร็จสิ้น")
            return redirect("/adminsys/addCamera")
        except:
            messages.error(request, "เกิดข้อผิดพลาดในการเพิ่มกล้อง")
            return redirect("/adminsys/addCamera")

    else:
        return render(request, 'adminsys/addCamera.html')

def deleteMember(request, id):
    try:
        user = User.objects.get(id=id)
        path = "media/dataset/"+user.first_name+"_"+user.last_name
        if os.path.exists(path):
            shutil.rmtree(path, ignore_errors=True)
        user.delete()
        messages.success(request, 'ลบสมาชิกเสร็จสิ้น')
        return redirect('/adminsys/showMember/1/')
    except:
        messages.error(request, "เกิดข้อผิดพลาดในการลบสมาชิก")
        return redirect('/adminsys/showMember/1/')

def deleteTeacher(request, id):
    try:
        Teacher.objects.get(id=id).delete()
        messages.success(request, 'ลบอาจารย์เสร็จสิ้น')
        return redirect('/adminsys/showTeacher/1/')
    except:
        messages.error(request, "เกิดข้อผิดพลาดในการลบอาจารย์")
        return redirect('/adminsys/showTeacher/1/')

def deleteCamera(request, id):
    try:
        Camera.objects.get(id=id).delete()
        messages.success(request, 'ลบกล้องเสร็จสิ้น')
        return redirect('/adminsys/showCamera/1/')
    except:
        messages.error(request, "เกิดข้อผิดพลาดในการลบกล้อง")
        return redirect('/adminsys/showCamera/1/')

def editMember(request, id):
    if request.method == "POST":
        firstname = request.POST.get('firstname', None)
        lastname = request.POST.get('lastname', None)
        addr = request.POST.get('address', None)
        phone = request.POST.get('phone', None)
        try:
            user = User.objects.get(id=id)
            user.first_name = firstname 
            user.last_name = lastname
            user.save()

            obj = Profile.objects.get(user=user)
            obj.address = addr
            obj.phone_no = phone
            obj.save()

            messages.success(request, "บันทึกการเปลี่ยนแปลงเสร็จสิ้น")
            return redirect(f'/adminsys/editMember/{id}/')
        except:
            messages.error(request, "ไม่พบผู้ใช้ไอดีนี้")
            return redirect(f'/adminsys/editMember/{id}/')
        
    else:
        try:
            user = User.objects.get(id=id)
            return render(request, 'adminsys/editMember.html', {'users': user})
        except:
            return redirect('/adminsys/showMember/1/')

def editImageProfileForAdmin(request, id):
    try:
        profile = Profile.objects.get(user=User.objects.get(id=id))
    except:
        return redirect('/adminsys/showMember/1/')
    image_in = request.FILES['imgfile']
    if str((image_in.name)[-3:]) in ['jpg', 'png', 'fif']:
        profile.image = image_in
        profile.save()
        messages.success(request, "บันทึกการเปลี่ยนแปลงเสร็จสิ้น")
        return redirect(f'/adminsys/editMember/{id}/')
    else:
        messages.error(request, "กรุณาอัพโหลดไฟล์ .png .jpg .jfif")
        return redirect(f'/adminsys/editMember/{id}/')

def editTeacher(request,id):
    if request.method == "POST":
        fname = request.POST['fname']
        lname = request.POST['lname']
        pwd = request.POST['password']
        tel = request.POST.get('phone_no', None)
        department = request.POST.get('department', None)
        teacher = Teacher.objects.get(id=id)
        if pwd != teacher.password:
            hashPassword = hashlib.sha256(pwd.encode("utf-8")).hexdigest()
            teacher.password = hashPassword
        teacher.firstname = fname
        teacher.lastname = lname
        teacher.phone_no = tel
        teacher.department = department

        teacher.save()
        messages.success(request, "บันทึกการเปลี่ยนแปลงเสร็จสิ้น")
        return redirect(f'/adminsys/editTeacher/{id}/')
        
    else:
        try:
            teacher = Teacher.objects.get(id=id)
            return render(request, 'adminsys/editTeacher.html', {'teacher':teacher})
        except:
            return redirect('/adminsys/showTeacher/1/')

def editCamera(request, id):
    if request.method == "POST":
        room = request.POST['room']
        link = request.POST['link']

        try:
            camera = Camera.objects.get(id=id)
            camera.NumberRoom = room
            camera.Link = link
            camera.save()
            messages.success(request, 'บักทึกการเปลี่ยนแปลงเสร็จสิ้น')
            return redirect(f'/adminsys/editCamera/{id}/')
        except:
            return redirect('/adminsys/showCamera/1/')
    else:
        try:
            camera = Camera.objects.get(id=id)
            return render(request, 'adminsys/editCamera.html', {'camera': camera})
        except:
            return redirect('/adminsys/showCamera/1/')

def addTeacherByFile(request):
    if request.method == "POST":
        excel_file = request.FILES['file']
        if str((excel_file.name)[-4:]) == "xlsx":
            df = pd.read_excel(excel_file)

        elif str((excel_file.name)[-3:]) == "csv":
            df = pd.read_csv(excel_file)
        else:
            messages.error(request, 'กรุณาอัพโหลดไฟล์ Excel')
            return redirect('showTeacher/1/')

        for i in range(len(df)):
            username = df['username'][i] 
            password = df['password'][i] 
            email = df['email'][i]
            fname = df['firstname'][i]
            lname = df['lastname'][i]
            department = df['department'][i]
            phone = "0" + str(df['phone_no'][i])

            hashPassword = hashlib.sha256(password.encode("utf-8")).hexdigest()
            # set value 
            teacher = Teacher(username=username, password=hashPassword, email=email, firstname=fname, lastname=lname, department=department, phone_no=phone)
            try:
                teacher.save()
            except:
                messages.error(request, f'เกิดข้อผิดพลาดที่ผู้ใช้ไอดี {username} รายชื่อก่อนหน้าได้ถูกบันทึกแล้ว')
                return redirect('/adminsys/showTeacher/0/')
            
        messages.success(request, 'อัพโหลดเสร็จสิ้น')
        return redirect('/adminsys/showTeacher/0/')

def addMemberByFile(request):
    if request.method == "POST":
        excel_file = request.FILES['file']
        if str((excel_file.name)[-4:]) == "xlsx":
            df = pd.read_excel(excel_file)
        elif str((excel_file.name)[-3:]) == "csv":
            df = pd.read_csv(excel_file)
        else:
            messages.error(request, 'กรุณาอัพโหลดไฟล์ที่เป็นนามสกุล .xlsx หรือ .csv')
            return redirect('/adminsys/showMember/1/')

        for i in range(len(df)):
            try:
                username = df['username'][i] 
                password = df['password'][i] 
                email = df['email'][i]
                fname = df['firstname'][i]
                lname = df['lastname'][i]
                addr = df['address'][i]
                phone = "0" + str(df['phone_no'][i])
            except:
                messages.error(request, f'เกิดข้อผิดพลาดที่ผู้ใช้ {username} กรุณาตรวจสอบคอลัมน์และแถวมีครบทุกช่องหรือไม่')
                return redirect('/adminsys/showMember/1/')

            try:
                user = User.objects.create_user(username=username, password=password, first_name=fname, last_name=lname, email=email)
                user.save()
            except:
                messages.error(request, f'เกิดข้อผิดพลาดที่ผู้ใช้ {username} Username หรือ Email อาจซ้ำ')
                return redirect('/adminsys/showMember/1/')


            profile = Profile(user=user, phone_no=phone, address=addr, approved=True)
            try:
                profile.save()
            except Exception as e:
                messages.error(request, "เกิดข้อผิดพลาดบางอย่าง")
                return redirect('/adminsys/showMember/1/')
        
        messages.success(request, 'อัพโหลดเสร็จสิ้น')
        return redirect('/adminsys/showMember/1/')

            