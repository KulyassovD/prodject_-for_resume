from django.contrib.auth import get_user_model
from django.test import Client, TestCase

User = get_user_model()


class PostModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(PostModelTest.user)

    def test_url_template(self):
        """URL-адрес использует соответствующий шаблон."""
        # Шаблоны по адресам
        test_url_names = {
            '/auth/signup/': 200,
            '/auth/logout/': 200,
            '/auth/login/': 200}
        for value, expected in test_url_names.items():
            with self.subTest(value=value):
                response = self.guest_client.get(value)
                self.assertEqual(response.status_code, expected)

    def test_urls_uses_correct_template(self):
        templates_url_names = {
            '/auth/logout/': 'users/logged_out.html',
            '/auth/login/': 'users/login.html'}
        for value, expected in templates_url_names.items():
            with self.subTest(value=value):
                response = self.authorized_client.get(value)
                self.assertTemplateUsed(response, expected)
