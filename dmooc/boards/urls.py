from django.urls import path
from .views import board_list, board_write, board_detail, board_delete, comment_write, likes
urlpatterns = [
    path('list/', board_list, name='board_list'),
    path('write/', board_write, name='board_write'),
    path('detail/<int:pk>/', board_detail, name='board_detail'),
    path('detail/<int:pk>/delete/', board_delete, name='board_delete'),
    path('comment_write/<int:board_id>', comment_write, name='comment_write'),
    path('like/<int:board_id>/', likes, name="likes"),
]