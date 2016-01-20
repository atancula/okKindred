from django.conf.urls import url
from comment.views import post_comment, get_comments

urlpatterns = [
    url(r'^post/$', post_comment, name='comments-post-comment'),
    url(r'^get/$', get_comments, name='comments-get-comment'),
]