from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path
from app import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('register/', views.register),  # done
    path('login/', views.login),  # done
    path('logout/', views.logout),  # done
    path('create_new_ad/', views.create_new_ad),  # done
    path('add_favourite_ads/', views.add_favourite_ads),
    path('update_profile/', views.update_profile),  # done
    path('update_ad/', views.update_ad),  # done
    path('delete_ad/', views.delete_ad), # done
    path('delete_favourite/', views.delete_favourite),
    path('my_profile/', views.my_profile),  # done
    path('user_profile/<username>', views.user_profile),
    path('my_ads/', views.my_ads),  # done
    path('ad_detail/<int:id>', views.ad_detail),  # reduntant
    path('get_image/<name>', views.get_image),  # done
    path('ads/', views.ads),  # done
    path('latest_ads/', views.latest_ads),  # done
    path('favourite_ads/', views.favourite_ads),
    path('check_email/', views.check_email),  # done
    path('check_username/', views.check_username),  # done
    path('get_districts/', views.get_districts),  # done
    path('get_categories/', views.get_categories),  # done
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
