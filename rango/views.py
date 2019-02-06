from django.shortcuts import render
from django.core.urlresolvers import reverse
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required

from django.http import HttpResponseRedirect, HttpResponse
from rango.models import Category, Page
from rango.forms import CategoryForm, PageForm, UserForm, UserProfileForm
from django.contrib.auth.models import User

# Create your views here.
def index(request):
    category_list = Category.objects.order_by('-likes')[:5]
    pages = Page.objects.order_by('-views')[:5]
    context_dict = {'categories': category_list, 'top_pages': pages, 'boldmessage': 'Crunchy, creamy, cookie, candy, cupcake!'}
    
    return render(request, 'rango/index.html', context=context_dict)
    
def about(request):
    context_dict = {'yourname': 'Mark R'}
    return render(request, 'rango/about.html', context=context_dict)
    

def register(request):
    # tell the template if registration successfull
    registered = False
    
    if request.method == 'POST':
        user_form = UserForm(data=request.POST)
        profile_form = UserProfileForm(data=request.POST)
        
        if user_form.is_valid() and profile_form.is_valid():
            user = user_form.save()
            
            user.set_password(user.password)
            user.save()
            
            # commit = False to delay saving the model until we can avoid integrity problems
            profile = profile_form.save(commit=False)
            profile.user = user
            
            if 'picture' in request.FILES:
                profile.picture = request.FILES['picture']
                
            profile.save()
            
            # tell template registration is successfull
            registered = True
        else:
            print(user_form.errors, profile_form.errors)
    else:
        # not a POST requestm render registration form with blank ModelForm instances
        user_form = UserForm()
        profile_form = UserProfileForm()
        
    return render(request,
                    'rango/register.html',
                    {'user_form': user_form,
                     'profile_form': profile_form,
                      'registered': registered})


def user_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        # if a user object returned, combaination valid
        user = authenticate(username=username, password=password)
        
        if user:
            if user.is_active:
                login(request, user)
                return HttpResponseRedirect(reverse('index'))
            else:
                return HttpResponse('Your Rango account is disabled')
        else:
            error_message = ''
            
            try:
                user = User.objects.get(username=username)
                print("Invalid password for user {}: {}".format(username, password))
                error_message = "Invalid password for user {}".format(username)
            except User.DoesNotExist:
                error_message = "User not found: {}".format(username)
                
            return render(request, 'rango/login.html', {'error_message': error_message})
    else:
        return render(request, 'rango/login.html', {})
       
       
@login_required        
def user_logout(request):
    logout(request)
    return HttpResponseRedirect(reverse('index'))
        
        
@login_required
def restricted(request):
    return render(request, 'rango/restricted.html', {})

    
def show_category(request, category_name_slug):
    context_dict = {}
    
    try:
        category = Category.objects.get(slug=category_name_slug)
        pages = Page.objects.filter(category=category)
        
        context_dict['pages'] = pages
        context_dict['category'] = category
    except (Category.DoesNotExist, Page.DoesNotExist) as e:
        context_dict['category'] = None
        context_dict['pages'] = None
        
    return render(request, 'rango/category.html', context=context_dict)


@login_required   
def add_category(request):
	form = CategoryForm
	
	if request.method == 'POST':
		form = CategoryForm(request.POST)
		
		if form.is_valid():
			cat = form.save(commit=True)
			return index(request)
		else:
			print(form.errors)
			
	return render(request, 'rango/add_category.html', {'form': form})


@login_required   
def add_page(request, category_name_slug):
    try:
        category = Category.objects.get(slug=category_name_slug)
    except Category.DoesNotExist:
        category = None
    
    form = PageForm
    if request.method == 'POST':
        form = PageForm(request.POST)
        if form.is_valid():
            if category:
                page = form.save(commit=False)
                page.category = category
                page.views = 0
                page.save()
                return show_category(request, category_name_slug)
        else:
            print(form.errors)
    
    context_dict = {'form':form, 'category': category}
    return render(request, 'rango/add_page.html', context_dict)