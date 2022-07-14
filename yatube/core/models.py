# core/models.py
from django.db import models


class CreatedModel(models.Model):
    created = models.DateTimeField(verbose_name='Дата публикации',
                                   auto_now_add=True,
                                   help_text='Дата публикации',
                                   db_index=True)

    class Meta:
        abstract = True


class PubDateModel(models.Model):
    pub_date = models.DateTimeField(verbose_name='Дата публикации',
                                    auto_now_add=True,
                                    help_text='Дата публикации',
                                    db_index=True)

    class Meta:
        abstract = True
