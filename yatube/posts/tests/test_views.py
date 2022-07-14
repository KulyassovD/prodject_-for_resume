import datetime

from django import forms
from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase
from django.urls import reverse

from ..models import Comment, Follow, Group, Post

User = get_user_model()


class PostModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.user2 = User.objects.create_user(username='auth2')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug',
            description='Тестовое описание',
        )
        cls.group_2 = Group.objects.create(
            title='Тестовая группа_2',
            slug='test-slug-2',
            description='Тестовое описание_2',
        )
        now = datetime.datetime.now()
        now_6 = now - datetime.timedelta(hours=6)
        small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        cls.uploaded = SimpleUploadedFile(
            name='small.gif',
            content=small_gif,
            content_type='image/gif'
        )
        cls.post2 = Post.objects.create(
            author=cls.user,
            text='Тестовый пост',
            group=PostModelTest.group,
            pub_date=now_6.strftime("%d %Y"),
            image=PostModelTest.uploaded
        )
        for fix in range(12):
            cls.post = Post.objects.create(
                author=cls.user,
                text='Тестовые посты в цикле',
                group=PostModelTest.group,
                pub_date=now_6.strftime("%d %Y"),
                image=PostModelTest.uploaded
            )
        cls.comment = Comment.objects.create(
            author=cls.user,
            text='Тестовый комент',
            post=PostModelTest.post2
        )

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client_2 = Client()
        self.authorized_client.force_login(PostModelTest.user)
        self.authorized_client_2.force_login(PostModelTest.user2)
        cache.clear()

    def test_pages_uses_correct_template(self):
        templates_pages_names = {
            'posts/index.html': reverse('posts:index'),
            'posts/group_list.html': (
                reverse('posts:group_list', kwargs={'slug': 'test-slug'})),
            'posts/profile.html': (
                reverse('posts:profile', kwargs={'username': 'auth'})),
            'posts/post_detail.html': (
                reverse('posts:post_detail', kwargs={'post_id': 1})),
            'posts/create_post.html': (
                reverse('posts:post_edit', kwargs={'post_id': 1}))}
        for template, reverse_name in templates_pages_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_index_show_correct_context(self):
        response = self.authorized_client.get(reverse('posts:index'))
        post = response.context['page_obj'][0]
        correct_context = {
            post.author: PostModelTest.user,
            post.text: 'Тестовый пост',
            post.group: PostModelTest.group,
            post.image: PostModelTest.post2.image,
            post.pub_date.strftime("%d %Y"): (
                PostModelTest.post.pub_date.strftime("%d %Y"))}
        for template, reverse_name in correct_context.items():
            with self.subTest(template=template):
                self.assertEqual(template, reverse_name)

    def test_group_list_show_correct_context(self):
        response = self.authorized_client.get(
            reverse('posts:group_list', kwargs={'slug': 'test-slug'}))
        group = response.context['page_obj'][0]
        group_gr = response.context['group']
        correct_context = {
            group.author: PostModelTest.user,
            group.pub_date.strftime("%d %Y"): (
                PostModelTest.post.pub_date.strftime("%d %Y")),
            group.text: 'Тестовый пост',
            group.image: PostModelTest.post2.image,
            group_gr.description: 'Тестовое описание',
            group_gr.title: 'Тестовая группа'}
        for template, reverse_name in correct_context.items():
            with self.subTest(template=template):
                self.assertEqual(template, reverse_name)

    def test_profile_show_correct_context(self):
        response = self.authorized_client.get(
            reverse('posts:profile', kwargs={'username': 'auth'}))
        author = response.context['page_obj'][0]
        author_aut = response.context['author']
        author_count = response.context['count']
        post_list = PostModelTest.user.posts.all()
        post_list_count = post_list.count()
        correct_context = {
            author.author: PostModelTest.user,
            author.pub_date.strftime("%d %Y"): (
                PostModelTest.post.pub_date.strftime("%d %Y")),
            author.text: 'Тестовый пост',
            author.image: PostModelTest.post2.image,
            author.group: PostModelTest.group,
            author_count: post_list_count,
            author_aut: PostModelTest.user}
        for template, reverse_name in correct_context.items():
            with self.subTest(template=template):
                self.assertEqual(template, reverse_name)

    def test_post_detail_show_correct_context(self):
        response = self.authorized_client.get(
            reverse('posts:post_detail', kwargs={'post_id': '1'}))
        post_detail = response.context['post']
        post_detail_count = response.context['count']
        post_list = PostModelTest.user.posts.all()
        post_list_count = post_list.count()
        correct_context = {
            post_detail.image: PostModelTest.post2.image,
            post_detail.author: PostModelTest.user,
            post_detail.text: 'Тестовый пост',
            post_detail.group: PostModelTest.group,
            post_detail.pub_date.strftime("%d %Y"): (
                PostModelTest.post.pub_date.strftime("%d %Y")),
            post_detail_count: post_list_count,
        }
        for template, reverse_name in correct_context.items():
            with self.subTest(template=template):
                self.assertEqual(template, reverse_name)

    def test_create_show_correct_context(self):
        response = self.authorized_client.get(reverse('posts:post_create'))
        correct_context = {
            'group': forms.fields.ChoiceField,
            'text': forms.fields.CharField}
        for value, expected in correct_context.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)

    def test_post_edit_correct_context(self):
        response = self.authorized_client.get(
            reverse('posts:post_edit', kwargs={'post_id': '1'}))
        correct_context = {
            'group': forms.fields.ChoiceField,
            'text': forms.fields.CharField}
        for value, expected in correct_context.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)

    def test_first_page_index_contains_ten_records(self):
        response = self.client.get(reverse('posts:index'))
        self.assertEqual(len(response.context['page_obj']), 10)

    def test_second_page_index_contains_three_records(self):
        response = self.client.get(reverse('posts:index') + '?page=2')
        self.assertEqual(len(response.context['page_obj']), 3)

    def test_first_page_group_list_contains_ten_records(self):
        response = self.authorized_client.get(
            reverse('posts:group_list', kwargs={'slug': 'test-slug'}))
        self.assertEqual(len(response.context['page_obj']), 10)

    def test_second_page_group_list_contains_three_records(self):
        response = self.authorized_client.get(reverse(
            ('posts:group_list'), kwargs={'slug': 'test-slug'}) + '?page=2')
        self.assertEqual(len(response.context['page_obj']), 3)

    def test_first_page_profile_contains_ten_records(self):
        response = self.authorized_client.get(
            reverse('posts:profile', kwargs={'username': 'auth'}))
        self.assertEqual(len(response.context['page_obj']), 10)

    def test_second_page_profile_contains_three_records(self):
        response = self.authorized_client.get(
            reverse('posts:profile', kwargs={'username': 'auth'}) + '?page=2')
        self.assertEqual(len(response.context['page_obj']), 3)

    def test_post_in_group(self):
        response = self.authorized_client.get(reverse('posts:index'))
        post_list = PostModelTest.group.posts.all()
        post_list_2 = PostModelTest.group_2.posts.all()
        self.assertEqual(response.context['page_obj'][0],
                         response.context.get('page_obj')[0])
        self.assertIn(response.context['page_obj'][0], post_list)
        self.assertNotIn(response.context['page_obj'][0], post_list_2)

    def test_follow_field(self):
        # Проверили, что сообщение из пидписки создалось с правильными полями
        user = PostModelTest.user2
        author = User.objects.get(username=PostModelTest.user)
        Follow.objects.create(user=user, author=author)
        response = self.authorized_client_2.get(reverse('posts:follow_index'))
        post = response.context['page_obj'][0]
        correct_context = {
            post.author: PostModelTest.user,
            post.text: 'Тестовый пост',
            post.group: PostModelTest.group,
            post.image: PostModelTest.post2.image,
            post.pub_date.strftime("%d %Y"): (
                PostModelTest.post.pub_date.strftime("%d %Y"))}
        for template, reverse_name in correct_context.items():
            with self.subTest(template=template):
                self.assertEqual(template, reverse_name)


    def test_coment(self):
        # Проверили, что сообщения появляются на странице корректно
        response = self.authorized_client.get(
            reverse('posts:post_detail', kwargs={'post_id': '1'}))
        post_detail_comment = response.context['page_comments'][0]
        correct_context = {
            post_detail_comment.author: PostModelTest.user,
            post_detail_comment.text: PostModelTest.comment.text
        }
        for template, reverse_name in correct_context.items():
            with self.subTest(template=template):
                self.assertEqual(template, reverse_name)

    def test_cache(self):
        post = Post.objects.create(
            text='test',
            author=self.user,
            group=self.group
        )
        index = reverse('posts:index')
        response = self.authorized_client.get(index)
        cached_response_content = response.content

        post.delete()

        response = self.authorized_client.get(index)
        self.assertEqual(cached_response_content, response.content)

        cache.clear()

        response = self.authorized_client.get(index)
        self.assertEqual(cached_response_content, response.content)

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        cls.group.delete()
        cls.group_2.delete()
        cls.comment.delete()
        cls.user.delete()
        cls.user2.delete()
