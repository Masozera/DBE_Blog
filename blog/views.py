from django.shortcuts import render,get_object_or_404
from .models import Post
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.views.generic import ListView
from .forms import EmailPostForm,CommentForm, SearchForm
from django.core.mail import send_mail
from taggit.models import Tag
from django.db.models import Count
from django.contrib.postgres.search import SearchVector,SearchQuery,SearchRank

# Create your views here.

def post_list(request, tag_slug=None):
    object_list = Post.published.all()

    tag = None
    if tag_slug:
        tag = get_object_or_404(Tag, slug=tag_slug)
        object_list = object_list.filter(tags__in=[tag])

    paginator = Paginator(object_list, 3) # 3 posts in each page
    page = request.GET.get('page')
    try:
        posts = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer deliver the first page
        posts = paginator.page(1)
    except EmptyPage:
        # If page is out of range deliver last page of results
        posts = paginator.page(paginator.num_pages)
    return render(request,'blog/post/list.html',{'page': page,'posts': posts,'tag':tag})

# class PostListView(ListView):
#     queryset = Post.published.all()
#     context_object_name = 'posts'
#     paginate_by = 3
#     template_name = 'blog/post/list.html'

def post_detail(request, year, month, day, post):
    post = get_object_or_404(Post, slug=post,status='published',publish__year=year,publish__month=month,
    publish__day=day)

    # List of active comments for this post
    comments = post.comments.filter(active=True)
    new_comment = None

    if request.method == 'POST':
        # A comment was posted
        comment_form = CommentForm(data=request.POST)
        if comment_form.is_valid():
            # Create Comment object but don't save to database yet
            new_comment = comment_form.save(commit=False)
            # Assign the current post to the comment
            new_comment.post = post
            # Save the comment to the database
            new_comment.save()
    else:
        comment_form = CommentForm()   # This is an emppty form on a get request

    post_tags_ids = post.tags.values_list('id', flat=True)  # retrieve a Python list of IDs for the tags of the current post
    similar_posts = Post.published.filter(tags__in=post_tags_ids).exclude(id=post.id) #You get all posts that contain any of these tags, excluding the current post itself.
    similar_posts = similar_posts.annotate(same_tags=Count('tags')).order_by('-same_tags','-publish')[:4] # You use the Count aggregation function to generate a calculated field—same_ tags—that contains the number of tags shared with all the tags queried.

    return render(request,'blog/post/detail.html',{'post': post,'comments': comments,'new_comment': new_comment,
    'comment_form': comment_form, 'similar_posts': similar_posts})


def post_share(request, post_id):
    # Retrieve post by id
    post = get_object_or_404(Post, id=post_id, status='published')
    sent = False

    if request.method == 'POST':
        # Form was submitted
        form = EmailPostForm(request.POST)
        if form.is_valid():
            # Form fields passed validation
            cd = form.cleaned_data
            post_url = request.build_absolute_uri(
            post.get_absolute_url())
            subject = f"{cd['name']} recommends you read " "{post.title}"
            message = f"Read {post.title} at {post_url}\n\n" f"{cd['name']}\'s comments: {cd['comments']}"
            send_mail(subject, message, 'masozeravictor@gmail.com',[cd['to']])
            sent = True
            # ... send email
    else:
        form = EmailPostForm()   # this is wen the page is loaded with a get request. An empty form appears
    return render(request, 'blog/post/share.html', {'post': post,'form': form})

def post_search(request):
    form = SearchForm()
    query = None
    results = []
    if 'query' in request.GET:  # To check whether the form is submitted, you look for the query parameter in the request.GET dictionary
        form = SearchForm(request.GET)   #  When the form is submitted, you instantiate it with the submitted GET data, and verify that the form data is valid
        if form.is_valid():
            query = form.cleaned_data['query']
            # results = Post.published.annotate(search=SearchVector('title', 'body'), ).filter(search=query)
            # search_vector = SearchVector('title', 'body')
            search_vector = SearchVector('title', weight='A') + SearchVector('body', weight='B')
            search_query = SearchQuery(query)
            # results = Post.published.annotate(search=search_vector,rank=SearchRank(search_vector, search_query)).filter(search=search_query).order_by('-rank')
            results = Post.published.annotate(rank=SearchRank(search_vector, search_query)).filter(rank__gte=0.3).order_by('-rank')
            # In the preceding code, you create a SearchQuery object, filter results by it, and
            # use SearchRank to order the results by relevancy. 
    return render(request,'blog/post/search.html',{'form': form,'query': query,'results': results})


    # You can boost specific vectors so that more weight is attributed to them when
    # ordering results by relevancy. For example, you can use this to give more relevance
    # to posts that are matched by title rather than by content.