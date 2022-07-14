from django import forms

from .models import Comment, Post


class PostForm(forms.ModelForm):
    class Meta:
        LANGUAGE_CODE = "ru"
        model = Post
        fields = ['group', 'text', 'image']
        widget = {
            'text': forms.Textarea(attrs={'cols': 40, 'rows': 10})
        }


class CommentForm(forms.ModelForm):
    class Meta:
        LANGUAGE_CODE = "ru"
        model = Comment
        fields = ('text',)
        labels = {
            'text': 'Текст',
        }
        help_texts = {
            'text': 'Текст нового комментария',
        }
