from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.test import Client, TestCase

from ..models import Group, Post

User = get_user_model()


class PostModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.user_2 = User.objects.create_user(username='authaa')
        cls.group = Group.objects.create(
            slug='test-slug',
        )
        cls.post = Post.objects.create(
            author=cls.user,
        )

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(PostModelTest.user)
        self.authorized_client_2 = Client()
        self.authorized_client_2.force_login(PostModelTest.user_2)
        cache.clear()

    def test_urls_template(self):
        templates_url_names = {
            '/': 200,
            '/group/test-slug/': 200,
            '/profile/auth/': 200,
            '/profile/auth/follow/': 302,
            '/profile/auth/unfollow/': 302,
            '/posts/1/': 200,
            '/posts/1/edit/': 302,
            '/posts/1/comment/': 302,
            '/create/': 302,
            '/enexisting_page/': 404}
        templates_url_names_aut = {
            '/': 200,
            '/group/test-slug/': 200,
            '/profile/auth/': 200,
            '/profile/auth/follow/': 302,
            '/profile/auth/unfollow/': 302,
            '/posts/1/': 200,
            '/posts/1/edit/': 200,
            '/create/': 200,
            '/enexisting_page/': 404}
        for value, expected in templates_url_names.items():
            with self.subTest(value=value):
                response = self.guest_client.get(value)
                self.assertEqual(response.status_code, expected)
        for value, expected in templates_url_names_aut.items():
            with self.subTest(value=value):
                response = self.authorized_client.get(value)
                self.assertEqual(response.status_code, expected)

    def test_urls_uses_redirect_template(self):
        templates_url_names = {
            '/posts/1/edit/': '/auth/login/?next=/posts/1/edit/',
            '/profile/auth/follow/': '/auth/login/?next=/profile/auth/follow/',
            '/create/': '/auth/login/?next=/create/'}
        for value, expected in templates_url_names.items():
            with self.subTest(value=value):
                response = self.guest_client.get(value)
                self.assertRedirects(response, expected)

    def test_urls_uses_correct_template(self):
        templates_url_names = {
            '/': 'posts/index.html',
            '/group/test-slug/': 'posts/group_list.html',
            '/profile/auth/': 'posts/profile.html',
            '/posts/1/': 'posts/post_detail.html',
            '/posts/1/edit/': 'posts/create_post.html',
            '/create/': 'posts/create_post.html'}
        for value, expected in templates_url_names.items():
            with self.subTest(value=value):
                response = self.authorized_client.get(value)
                self.assertTemplateUsed(response, expected)

    def test_urls_uses_redirect_no_author_template(self):
        templates_url_names = {
            '/posts/1/edit/': '/posts/1/'}
        for value, expected in templates_url_names.items():
            with self.subTest(value=value):
                response = self.authorized_client_2.get(value)
                self.assertRedirects(response, expected)
