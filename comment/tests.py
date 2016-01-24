from django.contrib.contenttypes.models import ContentType
from django.test import TestCase
from django.test.utils import override_settings

from custom_user.models import User
from family_tree.models import Family, Person

from comment.models import Comment
from comment.views import _get_when_posted

from django.utils import timezone
import datetime

@override_settings(SECURE_SSL_REDIRECT=False)
class CommentsTestCase(TestCase): # pragma: no cover
    '''
    This defines all the tests for comments app
    '''

    def setUp(self):
        '''
        Sets up some default data for testing
        '''
        self.family = Family()
        self.family.save()

        self.user = User.objects.create_user(email='anastasiasteele@example.com', password='50shades', name='anastasia steele', family_id=self.family.id)
        self.user.is_confirmed = True
        self.user.save()

        self.person = Person(name='anastasia steele', gender='F', user_id=self.user.id, email='anastasiasteele@example.com', family_id=self.family.id)
        self.person.save()


    def test_save_comment(self):
        '''
        Test that a comment can be saved and that the default data is populated
        '''

        # a user commenting on her own profile
        comment = Comment(
                content_object = self.person,
                user = self.user,
                ip_address = '192.168.0.1',
                comment = 'the muscles inside the deepest darkest part of me clench in the most delicous fashion')

        comment.save()

        self.assertEqual(self.person.id, comment.person.id)
        self.assertEqual(self.family.id, comment.family.id)


    def test_post_comment_view(self):
        '''
        Test that a comment can be posted
        '''
        self.client.login(email='anastasiasteele@example.com', password='50shades')
        response = self.client.post('/comment/post/',
        {
            'content_type': 'family_tree.person',
            'object_id': self.person.id,
            'comment': 'hello!'
        })

        self.assertEqual(200, response.status_code)
        self.assertEqual('hello!', response.json()[0]['comment'])

    def test_another_family_cannot_post_comment(self):
        '''
        Test that someone in another family cannot post on person's profile
        '''

        family = Family()
        family.save()
        user = User.objects.create_user(email='buffy@example.com', password='summers', name='buffy summer', family_id=family.id)
        user.is_confirmed = True
        user.save()

        self.client.login(email='buffy@example.com', password='summers')
        response = self.client.post('/comment/post/',
        {
            'content_type': 'family_tree.person',
            'object_id': self.person.id,
            'comment': 'Xander!'
        })

        self.assertEqual(404, response.status_code)

    def test_get_comments(self):
        '''
        Test that a comment can be read
        '''

        content_type = ContentType.objects.get(model='person')

        comment = Comment(
                    content_type = content_type,
                    object_id = self.person.id,
                    user = self.user,
                    ip_address = '192.168.0.1',
                    comment = 'demolition man')
        comment.save()

        self.client.login(email='anastasiasteele@example.com', password='50shades')

        response = self.client.get('/comment/get/',
        {
            'content_type': 'family_tree.person',
            'object_id': self.person.id,
        })

        self.assertEqual(200, response.status_code)
        self.assertEqual(comment.id, response.json()[0]['id'])
        self.assertEqual('demolition man', response.json()[0]['comment'])


    def test_another_family_cannot_get_comment(self):
        '''
        Test that someone in another family cannot get comments from another family's profile
        '''

        family = Family()
        family.save()
        user = User.objects.create_user(email='buffy@example.com', password='summers', name='buffy summer', family_id=family.id)
        user.is_confirmed = True
        user.save()

        self.client.login(email='buffy@example.com', password='summers')
        response = self.client.get('/comment/get/',
        {
            'content_type': 'family_tree.person',
            'object_id': self.person.id,
        })

        self.assertEqual(404, response.status_code)


    def test_delete_comment(self):
        '''
        Test that a comment can be deleted
        '''

        content_type = ContentType.objects.get(model='person')

        comment = Comment(
                    content_type = content_type,
                    object_id = self.person.id,
                    user = self.user,
                    ip_address = '192.168.0.1',
                    comment = 'demolition man')
        comment.save()

        self.client.login(email='anastasiasteele@example.com', password='50shades')

        response = self.client.post('/comment/delete/',
        {
            'id': comment.id
        })

        self.assertEqual(200, response.status_code)
        self.assertEqual(b'OK', response.content)
        self.assertEqual(0, Comment.objects.count())

    def test_another_family_cannot_delete_comment(self):
        '''
        Test that a comment can not be deleted by another family
        '''

        content_type = ContentType.objects.get(model='person')

        comment = Comment(
                    content_type = content_type,
                    object_id = self.person.id,
                    user = self.user,
                    ip_address = '192.168.0.1',
                    comment = 'demolition man')
        comment.save()

        family = Family()
        family.save()
        user = User.objects.create_user(email='clara@example.com', password='fray', name='clara fray', family_id=family.id)
        user.is_confirmed = True
        user.save()

        self.client.login(email='clara@example.com', password='fray')

        response = self.client.post('/comment/delete/',
        {
            'id': comment.id
        })

        self.assertEqual(404, response.status_code)
        self.assertEqual(comment.id, Comment.objects.get(id=comment.id).id)

    def test_get_when_posted(self):
        '''
        Tests the different comment dates
        '''

        language = 'en';

        self.assertEqual('10 seconds ago', _get_when_posted(timezone.now() - datetime.timedelta(seconds=10), language))
        self.assertEqual('1 minute ago', _get_when_posted(timezone.now() - datetime.timedelta(seconds=80), language))
        self.assertEqual('15 minutes ago', _get_when_posted(timezone.now() - datetime.timedelta(seconds=950), language))
        self.assertEqual('1 hour ago', _get_when_posted(timezone.now() - datetime.timedelta(seconds=4000), language))
        self.assertEqual('4 hours ago', _get_when_posted(timezone.now() - datetime.timedelta(hours=4.2), language))
        self.assertEqual('1 day ago', _get_when_posted(timezone.now() - datetime.timedelta(days=1), language))
        self.assertEqual('6 days ago', _get_when_posted(timezone.now() - datetime.timedelta(days=6), language))
        self.assertEqual('1 week ago', _get_when_posted(timezone.now() - datetime.timedelta(days=10), language))
        self.assertEqual('3 weeks ago', _get_when_posted(timezone.now() - datetime.timedelta(days=22), language))
        self.assertEqual('1 month ago', _get_when_posted(timezone.now() - datetime.timedelta(days=40), language))
        self.assertEqual('2 months ago', _get_when_posted(timezone.now() - datetime.timedelta(days=70), language))
        self.assertEqual('1 year ago', _get_when_posted(timezone.now() - datetime.timedelta(days=400), language))
        self.assertEqual('5 years ago', _get_when_posted(timezone.now() - datetime.timedelta(days=1900), language))
