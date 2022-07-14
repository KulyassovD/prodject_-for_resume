from core.models import CreatedModel, PubDateModel
from django.contrib.auth import get_user_model
from django.db import models

User = get_user_model()


class Group(models.Model):
    title = models.CharField(verbose_name='Заголовок',
                             max_length=200,
                             help_text='Название группы')
    slug = models.SlugField(
        verbose_name='Уникальный адрес страницы',
        unique=True, help_text=(
            'Укажите уникальный адрес для страницы задачи. Используйте только '
            'латиницу, цифры, дефисы и знаки подчёркивания'))
    description = models.TextField(verbose_name='Описание',
                                   max_length=400,
                                   help_text='Опишите группу')

    def __str__(self):
        return self.title


class Post(PubDateModel):
    text = models.TextField(verbose_name='Текст',
                            help_text='Напишите текст')
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='posts',
        verbose_name='Автор',
        help_text='Никнейм автора')
    group = models.ForeignKey(Group,
                              on_delete=models.SET_NULL,
                              blank=True,
                              null=True,
                              related_name='posts',
                              verbose_name='Группа',
                              help_text='Название группы')
    image = models.ImageField(
        'Картинка',
        upload_to='posts/',
        blank=True,
        help_text='Картинка'
    )

    def __str__(self):
        return self.text[:15]


class Comment(CreatedModel):
    post = models.ForeignKey(Post,
                             on_delete=models.CASCADE,
                             related_name='comments')
    author = models.ForeignKey(User,
                               on_delete=models.CASCADE,
                               related_name='comments')
    text = models.TextField('Текст', help_text='Текст нового комментария')


class Follow(models.Model):
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='following',
        verbose_name='Автор',
        help_text='Никнейм автора'
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='follower',
        verbose_name='Подписчик',
        help_text='Никнейм подписчика'
    )


class Meta:
    ordering = ('-pub_date',)
    verbose_name = 'Пост'
    verbose_name_plural = 'Посты'
    contreins = [
        models.CheckConstraint(
            name='Check follow',
            check=models.Q(models.F('author') != models.F('user'))),
        models.UniqueConstraint(
            name="Проверка единственности подписки",
            fields=["user", "author"],
        ),
    ]
