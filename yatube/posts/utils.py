from django.core.paginator import Paginator
from .constants import POSTS_PER_PAGE


def get_page_context(request, post_list, count_post=POSTS_PER_PAGE):
    paginator = Paginator(post_list, count_post)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return page_obj
