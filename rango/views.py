from django.shortcuts import render
from django.http import HttpResponse
from rango.models import Category

# Create your views here.
def index(request):
	category_list = Category.objects.order_by('-likes')[:5]
	context_dir = {'categories': category_list}
	
	return render(request, 'rango/index.html', context=context_dir)