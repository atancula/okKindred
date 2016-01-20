from django.contrib.contenttypes.models import ContentType
from django.test import TestCase
from django.test.utils import override_settings

from custom_user.models import User
from family_tree.models import Family, Person

from comment.models import Comment

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
        self.assertEqual('hello!', response.json()['comment'])

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
        Test that a comment can be posted
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

