from django.apps import apps
from django.contrib.auth.decorators import login_required
from django.http import Http404, HttpResponse
from django.contrib.contenttypes.models import ContentType
from django.views.decorators.http import require_POST, require_GET

from comment.models import Comment

import datetime
import json

'''
Taken from https://github.com/django/django-contrib-comments/blob/master/django_comments/views/comments.py
'''

ALLOWED_OBJECTS = ('person', 'image', 'gallery')

date_handler = lambda obj: (
    obj.isoformat()
    if isinstance(obj, datetime.datetime)
    or isinstance(obj, datetime.date)
    else None
)

@login_required
@require_POST
def post_comment(request):
    '''
    Posts a comment
    '''
    data = request.POST.copy()

    try:
        # Look up the object we're trying to comment about
        ctype = data.get("content_type")
        object_id = data.get("object_id")
        model_name = ctype.split('.')[1]

        # Only allow comments for certain objects
        if model_name in ALLOWED_OBJECTS:
            content_type = ContentType.objects.get(model=model_name)
            model = apps.get_model(ctype)
            target = model._default_manager.get(pk=object_id)
        else:
            raise Http404

    except:
        raise Http404

    # Ensure user is from same family as object being commented on
    if target.family_id != request.user.family_id:
        raise Http404

    #Create the comment
    comment = Comment(
        content_type = content_type,
        object_id = object_id,
        user = request.user,
        ip_address = request.META.get("REMOTE_ADDR", None),
        comment = data.get("comment"))

    comment.save()

    data = {
            'id': comment.id,
            'name': comment.person.name,
            'thumb': str(comment.person.small_thumbnail),
            'comment': comment.comment,
            'creation_date': comment.creation_date
           }

    return HttpResponse(json.dumps(data, default=date_handler), content_type="application/json")

@login_required
@require_GET
def get_comments(request):
    '''
    Gets the comments
    '''

    data = request.GET.copy()

    try:
        # Look up the object we're trying to comment about
        ctype = data.get("content_type")
        object_id = data.get("object_id")
        model_name = ctype.split('.')[1]

        # Only allow comments for certain objects
        if model_name in ALLOWED_OBJECTS:
            content_type = ContentType.objects.get(model=model_name)
            model = apps.get_model(ctype)
            target = model._default_manager.get(pk=object_id)
        else:
            raise Http404

    except:
        raise Http404


    # Ensure user is from same family as object being commented on
    if target.family_id != request.user.family_id:
        raise Http404

    comments = Comment.objects.select_related('person').filter(content_type=content_type, object_id=object_id).order_by('-creation_date')

    data = [];

    for comment in list(comments):
        data.append({
                    'id': comment.id,
                    'name': comment.person.name,
                    'thumb': str(comment.person.small_thumbnail),
                    'comment': comment.comment,
                    'creation_date': str(comment.creation_date)
                   })


    return HttpResponse(json.dumps(data), content_type="application/json")


@login_required
@require_POST
def delete_comment(request):
    '''
    deletes a comment
    '''
    data = request.POST.copy()

    try:
        # Look up the object we're trying to delete
        id = data.get("id")
        comment = Comment.objects.get(id=id)

    except:
        raise Http404

    # Ensure user is from same family as object being commented on
    if comment.family_id != request.user.family_id:
        raise Http404

    #Create the comment
    comment.delete()

    return HttpResponse("OK")
