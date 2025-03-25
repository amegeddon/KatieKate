from django.shortcuts import render, redirect, reverse, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.db.models.functions import Lower
from .models import GalleryImage, Category
#from .forms import GalleryImageForm  # You'll need to create this form for adding gallery items

def all_gallery_images(request):
    """ A view to show all gallery images, including sorting and search queries """
    
    gallery_images = GalleryImage.objects.all()
    categories = None
    query = None
    sort = None
    direction = None

    if request.GET:
        # Handle sorting
        if 'sort' in request.GET:
            sortkey = request.GET['sort']
            sort = sortkey
            if sortkey == 'title':
                sortkey = 'lower_title'
                gallery_images = gallery_images.annotate(lower_title=Lower('title'))
            
            if sortkey == 'category':
                sortkey = 'category__name'
            
            if 'direction' in request.GET:
                direction = request.GET['direction']
                if direction == 'desc':
                    sortkey = f'-{sortkey}'
            
            gallery_images = gallery_images.order_by(sortkey)

        # Handle filtering by category
        if 'category' in request.GET:
            categories_param = request.GET['category']
            categories = categories_param.split(',')
            gallery_images = gallery_images.filter(category__name__in=categories)
            categories = Category.objects.filter(name__in=categories)  # Filter categories

            print("Filtered Categories:", categories)  # Debugging statement to see selected categories

        # Handle search query (if needed in the future)
        if 'q' in request.GET:
            query = request.GET['q']
            if not query:
                messages.error(request, "You didn't enter any search criteria!")
                return redirect(reverse('gallery'))
            
            queries = Q(title__icontains=query) | Q(description__icontains=query)
            gallery_images = gallery_images.filter(queries)

    current_sorting = f'{sort}_{direction}' if sort and direction else 'None_None'

    # Fetch all categories by default if `categories` is None after processing GET parameters
    if categories is None:
        categories = Category.objects.all()

    context = {
        'gallery_images': gallery_images,
        'search_term': query,
        'current_categories': categories,
        'current_sorting': current_sorting,
    }

    print("Context passed to template:", context)  # Debugging the context

    return render(request, 'gallery/gallery.html', context)
