from django.urls import path
from . import views


urlpatterns = [
    path('create-student', views.create_student, name='create_student'), 
    path('get-students', views.get_all_students, name='get_all_students'),
    path('get-student/<uuid:id>', views.get_student, name='get_student'), 
    path('update-student/<uuid:id>', views.update_student, name='update_student'),
    path('delete-student/<uuid:id>', views.delete_student, name='delete_student'),
    path('students/<uuid:id>/summary/', views.generate_student_summary, name='generate_student_summary'),
    path('delete-student', views.delete_List_student, name= "delete_List_student")
]