from django.urls import path
from . import views

urlpatterns = [
    path('', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('admin_dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('delete_building/<str:building_code>/', views.delete_building, name='delete_building'),
    path('delete_cd/<int:pidm>/', views.delete_cd, name='delete_cd'),
    path('delete_student/<int:stud_ID>/', views.delete_student, name='delete_student'),
    path('delete_room/<int:room_num>/<str:building_code>/', views.delete_room, name='delete_room'),
    path('delete_lease/<int:stud_ID>/<int:room_num>/', views.delete_lease, name='delete_lease'),
    path('cd_dashboard/', views.cd_dashboard, name='cd_dashboard')
]
