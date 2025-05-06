from django.contrib import admin
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from ODApp.views import HomeView, Logines, SignUp, About ,Mainpage , Contactpage,live_detection_page,live_feed_view,upload_video,detect_image,video_result
urlpatterns = [
    path("admin/", admin.site.urls),
    path("home/", HomeView, name="home"),  # ✅ No 'views.' needed
    path("logins/", Logines, name="logins"),  # ✅ Use correct function name
    path("SignUp/", SignUp, name="SignUp"),
    path("About/", About, name="About"),
    path("Mainpage/", Mainpage, name="Mainpage"),
    path("Contact/", Contactpage, name="Contact"),
    path('live_detection/',live_detection_page, name='live_detection'),
    path('live_feed/', live_feed_view, name='live_feed'),

    path('detect_image/', detect_image, name='detect_image'),
    path('upload_video/', upload_video, name='upload_video'),
    path('upload_video/result/', video_result, name='video_result'),


] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT) + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)