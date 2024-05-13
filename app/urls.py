from . import views
from django.urls import path

urlpatterns = [
    path('',views.index),
    path('dashboard',views.dashboard,name='dashboard'),
    path('upload_file',views.upload_file,name='upload_file'),
    path('logout_user',views.logout_user,name='logout_user'),
    path('file_upload_result_one',views.file_upload_result_one,name='file_upload_result_one'),
    path('file_upload_result_two',views.file_upload_result_two,name='file_upload_result_two'),
    path('file_upload_result_three',views.file_upload_result_three,name='file_upload_result_three'),
    path('input',views.input,name='input'),
    path('graph',views.graph,name='graph'),
    path('graph_one',views.graph_one,name='graph_one'),
    path('graph_two',views.graph_two,name='graph_two'),
    path('graph_three',views.graph_three,name='graph_three'),
    path('pie_chart', views.pie_chart, name='pie_chart'),
    path('gggraph', views.gggraph, name='gggraph'),
    



]