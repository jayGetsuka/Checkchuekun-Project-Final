from django.urls import path, re_path
from . import views
from django.conf.urls.static import static
from django.conf import settings
from django.views.generic import TemplateView

urlpatterns = [
    path('', views.Login, name="login"),
    path('register', views.register, name="register"),
    path('logout', views.Logout, name="logout"),
    path('course_reg', views.course_reg, name="course_reg"),
    path('update_detail_profile', views.update_detail_profile, name="update_detail_profile"),
    path('update_image_profile', views.update_image_profile, name="update_image_profile"),
    path('search_course', views.searchCourse, name="search_course"),
    path('register_course/<int:id>', views.registerCourse),
    path('upload_for_train/', views.uploadForTrain, name="upload_for_train"),
    path('history_enroll/<int:num_page>/', views.historyEnroll, name="history_enroll"),
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)