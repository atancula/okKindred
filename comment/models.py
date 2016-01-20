from django.conf import settings
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models

from family_tree.models import Family, Person

COMMENT_MAX_LENGTH = getattr(settings, 'COMMENT_MAX_LENGTH', 3000)

'''
Taken from https://github.com/django/django-contrib-comments/blob/master/django_comments/models.py
'''

class CommentManager(models.Manager):
    def for_model(self, model):
        """
        QuerySet for all comments for a particular model (either an instance or
        a class).
        """
        ct = ContentType.objects.get_for_model(model)
        qs = self.get_queryset().filter(content_type=ct)
        if isinstance(model, models.Model):
            qs = qs.filter(object_pk=model._get_pk_val())
        return qs


class Comment(models.Model):
    '''
    Object that represents a comment
    '''

    # Content-object field
    content_type = models.ForeignKey(ContentType, related_name="content_type_set_for_%(class)s")
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')

    user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name="%(class)s_comments", null=False)
    person = models.ForeignKey(Person, null=False) #Use of model string name to prevent circular import
    family = models.ForeignKey(Family, null=False) #Use of model string name to prevent circular import

    comment = models.TextField(max_length=3000)

    #Tracking
    ip_address = models.GenericIPAddressField(unpack_ipv4=True, blank=True, null=True)
    creation_date = models.DateTimeField(auto_now_add=True, db_index=True)
    last_updated_date = models.DateTimeField(auto_now=True)

    # Manager
    objects = CommentManager()

    class Meta:
        ordering = ('creation_date',)

    def __str__(self):
        return "%s: %s..." % (self.user, self.comment[:50])

    def save(self, *args, **kwargs):
        '''
        Set the family and person on save automatically to allow fewer joins when getting profile info on comments
        '''
        self.person = Person.objects.get(user_id = self.user_id)
        self.family_id = self.user.family_id
        super(Comment, self).save(*args, **kwargs)

