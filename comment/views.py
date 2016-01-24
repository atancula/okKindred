from django.apps import apps
from django.contrib.auth.decorators import login_required
from django.http import Http404, HttpResponse
from django.contrib.contenttypes.models import ContentType
from django.views.decorators.http import require_POST, require_GET
from django.utils import translation

from comment.models import Comment

from django.utils import timezone

import json

'''
Taken from https://github.com/django/django-contrib-comments/blob/master/django_comments/views/comments.py
'''

ALLOWED_OBJECTS = ('person', 'image', 'gallery')

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

    data = [];
    data.append({
            'id': comment.id,
            'person_id' : comment.person.id,
            'person_name': comment.person.name,
            'thumb': str(comment.person.small_thumbnail),
            'comment': comment.comment,
            'creation_date': _get_when_posted(comment.creation_date, request.user.language)
           });

    return HttpResponse(json.dumps(data), content_type="application/json")

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

    comments = Comment.objects.select_related('person').filter(content_type=content_type, object_id=object_id).order_by('creation_date')

    data = [];

    for comment in list(comments):
        data.append({
                    'id': comment.id,
                    'person_id' : comment.person.id,
                    'person_name': comment.person.name,
                    'thumb': str(comment.person.small_thumbnail),
                    'comment': comment.comment,
                    'creation_date': _get_when_posted(comment.creation_date, request.user.language)
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

def _get_when_posted(creation_date, language):
    '''
    Returns a human readable format for when comment was posted
    '''
    translation.activate(language)

    time_diff = (timezone.now() - creation_date)

    # Less than a minute
    if (time_diff.total_seconds() < 60):
        return translation.ugettext('{0} seconds ago').format(int(time_diff.total_seconds()))

    # Less than 2 minutes
    if (time_diff.total_seconds() < 120):
        return translation.ugettext('1 minute ago')

    # Less than an hour
    if (time_diff.total_seconds() < 3600):
        return translation.ugettext('{0} minutes ago').format(int(time_diff.total_seconds() // 60))

    # Less than 2 hours
    if (time_diff.total_seconds() < 7200):
        return translation.ugettext('1 hour ago')

    # less than a day
    if (time_diff.days < 1):
        return translation.ugettext('{0} hours ago').format(int(time_diff.total_seconds() // 3600))

    # less than two days
    if (time_diff.days < 2):
        return translation.ugettext('1 day ago')

    # less than week
    if (time_diff.days < 7):
        return translation.ugettext('{0} days ago').format(time_diff.days)

    # less two weeks
    if (time_diff.days < 14):
        return translation.ugettext('1 week ago')

    # less than a month
    if (time_diff.days < 31):
        return translation.ugettext('{0} weeks ago').format(int(time_diff.days // 7))

    # less than two months
    if (time_diff.days < 60):
        return translation.ugettext('1 month ago')

    # less than a year
    if (time_diff.days < 365):
        return translation.ugettext('{0} months ago').format(int(time_diff.days // 30))

    # less than two years
    if (time_diff.days < 731):
        return translation.ugettext('1 year ago')

    # return number of years
    return translation.ugettext('{0} years ago').format(int(time_diff.days // 365))
