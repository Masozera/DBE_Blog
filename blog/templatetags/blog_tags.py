from django import template
from ..models import Post
from django.db.models import Count

#  template tags come in very handy when you need to add a functionality to
#  your templates that is not covered by the core set of Django template tags

register = template.Library()

@register.simple_tag
def total_posts():
    return Post.published.count()


@register.inclusion_tag('blog/post/latest_posts.html')
def show_latest_posts(count=5):
    latest_posts = Post.published.order_by('-publish')[:count]
    return {'latest_posts': latest_posts}

# Using an inclusion tag, you can render a template with context variables returned by your template tag. 

@register.simple_tag
def get_most_commented_posts(count=5):
    return Post.published.annotate(total_comments=Count('comments')).order_by('-total_comments')[:count]

# using the annotate() function to aggregate the total number of comments for each post. 
# You use the Count aggregation function to store the number of comments in the computed field total_ comments for each Post object. 
# You order the QuerySet by the computed field in descending order. 
# You also provide an optional count variable to limit the total
# number of objects returned.