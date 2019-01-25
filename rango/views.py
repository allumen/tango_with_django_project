from django.shortcuts import render
from django.http import HttpResponse
from rango.models import Category, Page

# Create your views here.
def index(request):
    category_list = Category.objects.order_by('-likes')[:5]
    pages = Page.objects.order_by('-views')[:5]
    context_dir = {'categories': category_list, 'top_pages': pages}
    
    return render(request, 'rango/index.html', context=context_dir)
    
def about(request):
    return HttpResponse('<a href="/rango/">Index</a><br>Rango says here is the about page.')

    
def show_category(request, category_name_slug):
    context_dict = {}
    
    try:
        category = Category.objects.get(slug=category_name_slug)
        pages = Page.objects.filter(category=category)
        
        context_dict['pages'] = pages
        context_dict['category'] = category
    except Category.DoesNotExist:
        context_dict['pages'] = None
        context_dict['category'] = None
        
    return render(request, 'rango/category.html', context_dict)