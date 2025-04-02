from django.shortcuts import render, redirect, reverse, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.db.models.functions import Lower
from .models import GalleryImage, Category
from .forms import GalleryForm


def all_gallery_images(request):
    """
    A view to display all gallery images, including sorting and search queries.

    """
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

    return render(request, 'gallery/gallery.html', context)


def gallery_detail(request, image_id):
    """
    A view to display the details of a single gallery image.

    This view fetches a specific image based on the image ID and renders the
    corresponding template with the image details.

    Args:
        request (HttpRequest): The request object.
        image_id (int): The ID of the image to be displayed.

    Returns:
        HttpResponse: The rendered 'gallery/gallery_detail.html' template with context.
    """
    image = get_object_or_404(GalleryImage, pk=image_id)

    context = {
        'image': image,
    }

    return render(request, 'gallery/gallery_detail.html', context)


@login_required
def add_gallery_image(request):
    """
    A view to add a new image to the gallery.

    This view handles form submission to add a new gallery image. Only superusers
    are allowed to add images. After a successful form submission, the user is redirected
    to the gallery page.

    Args:
        request (HttpRequest): The request object containing POST data.

    Returns:
        HttpResponse: The rendered 'gallery/add_gallery_image.html' template with context.
    """
    if not request.user.is_superuser:
        messages.error(request, 'Sorry, only store owners can do that.')
        return redirect(reverse('home'))

    if request.method == 'POST':
        form = GalleryForm(request.POST, request.FILES)
        if form.is_valid():
            gallery_image = form.save()
            messages.success(request, 'Successfully added Gallery Item!')
            return redirect(reverse('gallery'))
        else:
            messages.error(request, 'Failed to add Gallery Item. Please ensure the form is valid.')
    else:
        form = GalleryForm()

    context = {
        'form': form,
    }

    return render(request, 'gallery/add_gallery_image.html', context)


@login_required
def edit_gallery_image(request, image_id):
    """
    A view to edit an existing gallery image.
    
    This view allows authenticated (superuser) users to edit the details of an existing gallery image,
    including its title, description, and category. After successful update, the user is redirected to the gallery.
    """
    
    if not request.user.is_superuser:
        messages.error(request, 'Sorry, only store owners can do that.')
        return redirect(reverse('home'))

    image = get_object_or_404(GalleryImage, pk=image_id)
    if request.method == 'POST':
        form = GalleryForm(request.POST, request.FILES, instance=image)
        if form.is_valid():
            form.save()
            messages.success(request, 'Successfully updated gallery image!')
            return redirect(reverse('gallery'))  # Redirect to gallery instead of product detail
        else:
            messages.error(request, 'Failed to update gallery image. Please ensure the form is valid.')
    else:
        form = GalleryForm(instance=image)
        messages.info(request, f'You are editing {image.title}')

    context = {
        'form': form,
        'image': image,
    }

    return render(request, 'gallery/edit_gallery_image.html', context)

@login_required
def delete_gallery_image(request, image_id):
    """
    A view to delete a gallery image.

    This view allows authenticated (superuser) users to delete a gallery image from the database.
    After the image is deleted, the user is redirected to the gallery page.
    """

    if not request.user.is_superuser:
        messages.error(request, 'Sorry, only store owners can do that.')
        return redirect(reverse('home'))

    image = get_object_or_404(GalleryImage, pk=image_id)
    image.delete()
    messages.success(request, 'Gallery image deleted!')
    return redirect(reverse('gallery'))


def gallery_full_view(request, image_id):
    """
    A view to display an individual gallery image in full view with next/previous navigation.

    This view shows a specific image in full view and provides navigation links to the previous and next image
    in the gallery, based on the image ID.
    """

    current_image = get_object_or_404(GalleryImage, pk=image_id)
    prev_image = GalleryImage.objects.filter(id__lt=current_image.id).last()
    next_image = GalleryImage.objects.filter(id__gt=current_image.id).first()

    context = {
        'current_image': current_image,
        'prev_image': prev_image,
        'next_image': next_image,
    }

    return render(request, 'gallery/gallery_full_view.html', context)
