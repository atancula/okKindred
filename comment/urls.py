from django.conf.urls import url
from comment.views import post_comment, get_comments, delete_comment

urlpatterns = [
    url(r'^post/$', post_comment, name='comments-post-comment'),
    url(r'^get/$', get_comments, name='comments-get-comment'),
    url(r'^delete/$', delete_comment, name='comments-delete-comment'),
]