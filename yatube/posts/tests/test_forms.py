from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase
from django.urls import reverse

from ..models import Group, Post

User = get_user_model()


class PostModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый пост',
            group=PostModelTest.group)

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(PostModelTest.user)

    def test_create_task(self):
        post_list = PostModelTest.user.posts.all()
        tasks_count = post_list.count()
        small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        uploaded = SimpleUploadedFile(
            name='small.gif',
            content=small_gif,
            content_type='image/gif'
        )
        form_data = {'text': 'Тестовый пост_2',
                     'group': PostModelTest.group,
                     'image': uploaded}
        self.authorized_client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True
        )
        self.assertEqual(tasks_count, post_list.count())
        self.authorized_client.get(
            reverse('posts:post_edit', kwargs={'post_id': '2'}))

    def test_post_edit_task(self):
        form_data = {'text': 'Тестовый пост_5'}
        self.authorized_client.post(
            reverse('posts:post_edit', kwargs={'post_id': '1'}),
            data=form_data,
            follow=True)
        self.assertTrue(
            Post.objects.filter(
                text='Тестовый пост_5',
            ).exists())

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        cls.group.delete()
        cls.user.delete()
