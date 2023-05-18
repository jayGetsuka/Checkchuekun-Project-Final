from django.urls import path, re_path
from . import views
from django.conf.urls.static import static
from django.conf import settings
from django.views.generic import TemplateView

urlpatterns = [
    path('', views.Login, name="indexAd"),
    path('confirm_user', views.confirmUser, name="confirmUser_for_admin"),
    path('logout', views.Logout, name="logout_for_admin"),
    path('confirmUser/<int:id>', views.confirmToMember),
    path('deleteUser/<int:id>', views.deleteUser),
    path('showMember/<int:num_page>/', views.ShowMember, name="show_memebr_for_admin"),
    path('showTeacher/<int:num_page>/', views.ShowTeacher, name="show_teacher_for_admin"),
    path('showCamera/<int:num_page>/', views.ShowCamera, name="show_camera_for_admin"),
    path('addMember', views.addMember, name="add_member_for_admin"),
    path('addTeacher', views.addTeacher, name="add_teacher_for_admin"),
    path('addCamera', views.addCamera, name="add_camera_for_admin"),
    path('deleteMember/<int:id>/', views.deleteMember, name="delete_member_for_admin"),
    path('deleteTeacher/<int:id>/', views.deleteTeacher, name="delete_teacher_for_admin"),
    path('deleteCamera/<int:id>/', views.deleteCamera, name="delete_camera_for_admin"),
    path('editMember/<int:id>/', views.editMember, name="edit_member_for_admin"),
    path('editImageProfileForAdmin/<int:id>/', views.editImageProfileForAdmin, name="edit_image_profile_for_admin"),
    path('editTeacher/<int:id>/', views.editTeacher, name="edit_teacher_for_admin"),
    path('editCamera/<int:id>/', views.editCamera, name="edit_camera_for_admin"),
    path('addTeacherByFile', views.addTeacherByFile, name="addTeacherFile"),
    path('addMemberByFile', views.addMemberByFile, name="addMemberFile"),
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)