from django.shortcuts import render, redirect
from teacher.models import *
from member.models import Profile
from django.contrib.auth.models import User
from adminsys.models import Camera
from django.http import HttpResponseRedirect
from django.db.models import Q
import hashlib
import os
import shutil
from django.contrib import messages #import messages

#get paths of each file in folder named Images
#Images here contains my data(folders of various persons)



# Create your views here.
def Login(request):
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']
        hashPassword = hashlib.sha256(password.encode("utf-8")).hexdigest()
        try:
            teacher = Teacher.objects.get(username=username, password=hashPassword)
            request.session['teacher'] = {
                'id': teacher.id,
                'first_name': teacher.firstname,
                'last_name': teacher.lastname,
                'email': teacher.email,
                'department': teacher.department,
                'phone_no': teacher.phone_no,
            }
            subject = Subject.objects.filter(Teacher=teacher)
            return render(request, 'teacher/index.html', {'subject':subject})
        
        except:
            messages.error(request, "ไม่พบผู้ใช้")
            return redirect("/teacher")
        
    else:
        if 'teacher' in request.session:
            subject = Subject.objects.filter(Teacher=Teacher.objects.get(id=request.session['teacher']['id']))
            return render(request, 'teacher/index.html', {'subject':subject})
        else:
            return render(request, 'teacher/index.html')

def addSubject(request):
    if request.method == "POST":
        subCode = request.POST['subCode']
        subName = request.POST['subName']
        subRoom = request.POST['subRoom']
        teacher = Teacher.objects.get(id=request.session['teacher']['id'])
        camera = Camera.objects.get(NumberRoom=subRoom)
        try:
            subject = Subject.objects.create(SubjectCode=subCode, SubjectName=subName, SubjectRoom=camera, Teacher=teacher)
            subject.save()
            return redirect('/teacher')
        except:
            messages.error(request, "กรุณาตรวจสอบรหัสวิชาเนื่องจากอาจซ้ำ")
            return redirect("/teacher/addCourse")
    else:
        return render(request, 'teacher/addCourse.html', {'rooms':Camera.objects.all()})

def Logout(request):
    try:
        if 'teacher' in request.session:
            del request.session['teacher']
            return redirect('/teacher')
    except:
        return redirect('/teacher')

def deleteSubject(request, id):
    Subject.objects.get(id=id).delete()
    messages.success(request, "ลบรายวิชาเสร็จสิ้น")
    return redirect('/teacher')

def confirmUser(request):
    user_unconfirm = Profile.objects.filter(approved=False)
    return render(request, 'teacher/confirm_user.html', {'user_unconfirm': user_unconfirm})

def confirmToMember(request, id):

    try:
        profile = Profile.objects.get(user__id=id)
        if not profile.folder_image:
            messages.error(request, "ไม่สามารถยืนยันได้เนื่องจากผู้ใช้กรอกยังไม่อัพโหลดภาพสำหรับจำจดใบหน้า")
            return redirect("/teacher/confirm_user")
        else:
            profile.approved = True
            profile.save()
            messages.success(request, "บันทึกเป็นสมาชิกเสร็จสิ้น")
            return redirect('/teacher/confirm_user')

    except:
        messages.error(request, "ไม่พบผู้ใช้งานไอดีนี้")
        return redirect('/teacher/confirm_user')

def deleteUser(request, id):
    try:
        user = User.objects.get(id=id)
        path = "media/dataset/"+user.first_name+"_"+user.last_name
        if os.path.exists(path):
            shutil.rmtree(path, ignore_errors=True)
        user.delete()
        messages.success(request, "ลบผู้ใช้งานไอดีเสร็จสิ้น")
        return redirect('/teacher/confirm_user')
    except:
        messages.error(request, "ไม่พบผู้ใช้งานไอดีนี้")
        return redirect('/teacher/confirm_user')

def listMember(request, id):
    subject = Subject.objects.get(id=id)
    users = ClassMember.objects.filter(subject=subject).select_related('user', 'subject')
    return render(request, 'teacher/list_member.html', {'users': users})

def deleteStudent(request, sid, uid):
    ClassMember.objects.get(subject=sid, user=uid).delete()
    return HttpResponseRedirect(f'/teacher/list_member/{sid}/')

def searchSubject(request):
    search_subject = request.GET.get('search')
    teacher = Teacher.objects.get(id=request.session['teacher']['id'])

    subjects = Subject.objects.filter(Q(SubjectCode__icontains=search_subject, Teacher=teacher) | Q(SubjectName__icontains=search_subject,Teacher=teacher))

    if subjects.exists():
        return render(request, 'teacher/index.html', {'subject':subjects})
    else:
        subject = Subject.objects.filter(Teacher=teacher)
        messages.error(request, "ไม่พบรายวิชา")
        return render(request, 'teacher/index.html', {'subject': subject})


def faceScan(request, subid):
    try:
        subject = Subject.objects.get(id = subid)
        try:
            classmember = ClassMember.objects.filter(subject=subject)
        except:
            messages.error(request, "ไม่มีสมาชิกในรายวิชานี้")
            return redirect("/teacher")
    except:
        messages.error(request, "ไม่พบรายวิชา")
        return redirect("/teacher")

    return render(request, 'teacher/faceScan.html', {'subject': subject, 'countMember': classmember.count()})
