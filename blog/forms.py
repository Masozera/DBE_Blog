from django import forms
from .models import Comment

class EmailPostForm(forms.Form):
    name = forms.CharField(max_length=25)
    email = forms.EmailField()
    to = forms.EmailField()
    comments = forms.CharField(required=False,widget=forms.Textarea)

class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ('name', 'email', 'body')

class SearchForm(forms.Form):
     query = forms.CharField()





<p class="tags"> Tags:{{post.tags.all|join:""}}</p>

from taggit.models import Tag
def post_list(request, tag_slug=None):
    

