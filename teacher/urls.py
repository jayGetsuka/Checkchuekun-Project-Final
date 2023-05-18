from django.urls import path, re_path
from . import views
from django.conf.urls.static import static
from django.conf import settings
from django.views.generic import TemplateView

urlpatterns = [
    path('', views.Login, name="indexT"),
    path('addCourse', views.addSubject, name="add_course"),
    path('logout', views.Logout, name="logoutT"),
    path('deleteSubject/<int:id>', views.deleteSubject, name="delete_sub"),
    path('confirm_user', views.confirmUser, name="confirm_user"),
    path('confirm_to_member/<int:id>', views.confirmToMember),
    path('delete_user/<int:id>', views.deleteUser),
    path('list_member/<int:id>/', views.listMember),
    path('delete_std/<int:sid>/<int:uid>', views.deleteStudent),
    path('search_course', views.searchSubject, name="searchCourseTeacher"),
    path('faceScan/<int:subid>/', views.faceScan, name="face_scan"),

]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)