from django.shortcuts import render, redirect, reverse, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from .models import Product, Category, SpecialOffer
from django.db.models.functions import Lower
from .forms import ProductForm


# Create your views here.

def all_products(request):
    """ A view to show all products, including sorting and search queries """

    products = Product.objects.all()
    categories = None
    query = None
    sort = None
    direction = None

    if request.GET:
        if 'sort' in request.GET:
            sortkey = request.GET['sort']
            sort = sortkey
            if sortkey == 'name':
                sortkey = 'lower_name'
                products = products.annotate(lower_name=Lower('name'))

            if sortkey == 'category':
                sortkey = 'category__name'

            if 'direction' in request.GET:
                direction = request.GET['direction']
                if direction == 'desc':
                    sortkey = f'-{sortkey}'
            products = products.order_by(sortkey)

        
        # Handle filtering by category
        if 'category' in request.GET:
            categories = request.GET['category'].split(',')
            products = products.filter(category__name__in=categories)
            categories = Category.objects.filter(name__in=categories)

            print("Filtered Categories:", categories)  # Debugging statement to see selected categories

        # Handle search query
        if 'q' in request.GET:
            query = request.GET['q']
            if not query:
                messages.error(request, "You didn't enter any search criteria!")
                return redirect(reverse('products'))
            queries = Q(name__icontains=query) | Q(description__icontains=query)
            products = products.filter(queries)

        if 'q' in request.GET:
            query = request.GET['q']
            if not query:
                messages.error(request, "You didn't enter any search criteria!")
                return redirect(reverse('products'))
            
            queries = Q(name__icontains=query) | Q(description__icontains=query)
            products = products.filter(queries)

    current_sorting = f'{sort}_{direction}'
    
    # Fetch all categories by default if `categories` is None after processing GET parameters
    if categories is None:
        categories = Category.objects.all()

    context = {
        'products': products,
        'search_term': query,
        'current_categories': categories,
        'current_sorting': current_sorting,
    }
    
    print("Context passed to template:", context)

    return render(request, 'products/products.html', context)


def product_detail(request, product_id):
    """ A view to show individual product details """

    product = get_object_or_404(Product, pk=product_id)

    context = {
        'product': product,
    }

    return render(request, 'products/product_detail.html', context)


@login_required
def add_product(request):
    """ Add a product to the store """
    if not request.user.is_superuser:
        messages.error(request, 'Sorry, only store owners can do that.')
        return redirect(reverse('home'))

    
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            product = form.save()
            messages.success(request, 'Successfully added product!')
            return redirect(reverse('product_detail', args=[product.id]))
        else:
            messages.error(request, 'Failed to add product. Please ensure the form is valid.')
    else:
        form = ProductForm()
        
    template = 'products/add_product.html'
    context = {
        'form': form,
    }

    return render(request, template, context)


@login_required
def edit_product(request, product_id):
    """ Edit a product in the store """
    if not request.user.is_superuser:
        messages.error(request, 'Sorry, only store owners can do that.')
        return redirect(reverse('home'))

    product = get_object_or_404(Product, pk=product_id)
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            form.save()
            messages.success(request, 'Successfully updated product!')
            return redirect(reverse('product_detail', args=[product.id]))
        else:
            messages.error(request, 'Failed to update product. Please ensure the form is valid.')
    else:
        form = ProductForm(instance=product)
        messages.info(request, f'You are editing {product.name}')

    template = 'products/edit_product.html'
    context = {
        'form': form,
        'product': product,
    }

    return render(request, template, context)


@login_required
def delete_product(request, product_id):
    """ Delete a product from the store """
    if not request.user.is_superuser:
        messages.error(request, 'Sorry, only store owners can do that.')
        return redirect(reverse('home'))

    product = get_object_or_404(Product, pk=product_id)
    product.delete()
    messages.success(request, 'Product deleted!')
    return redirect(reverse('products'))

def special_offer_products(request, offer_name=None):
    """ A view to filter products by special offers (e.g., new_arrivals, deals, clearance) and allow sorting """
    
    # Initially fetch all products with a special offer assigned
    products = Product.objects.filter(special_offer__isnull=False)
    
    # If a specific offer name is provided, filter products by that special offer
    if offer_name:
        special_offer = SpecialOffer.objects.filter(name=offer_name).first()
        
        if special_offer:
            # Filter products based on the special offer
            products = products.filter(special_offer=special_offer)
        else:
            products = Product.objects.none()  # If no offer matches, show no products
            
              # Handle filtering by category
        if 'category' in request.GET:
            categories = request.GET['category'].split(',')
            products = products.filter(category__name__in=categories)
            categories = Category.objects.filter(name__in=categories)

            print("Filtered Categories:", categories)  # Debugging statement to see selected categories

    # Sorting logic
    sort = None
    direction = 'asc'  # Default sorting direction is ascending
    sortkey = 'name'   # Default sort key is by name
    
    if 'sort' in request.GET:
        sort = request.GET['sort']
        if sort == 'name':
            sortkey = 'lower_name'
            products = products.annotate(lower_name=Lower('name'))
        elif sort == 'price':
            sortkey = 'price'
        elif sort == 'rating':
            sortkey = 'rating'
        elif sort == 'category':
            sortkey = 'category__name'

        # Direction handling
        if 'direction' in request.GET:
            direction = request.GET['direction']
            if direction == 'desc':
                sortkey = f'-{sortkey}'

    # Apply sorting to the queryset
    products = products.order_by(sortkey)
    
    # Get all special offers for the sidebar or navigation
    special_offers = SpecialOffer.objects.all()

    # Adding sorting info to the context
    current_sorting = f'{sort}_{direction}'

    context = {
        'products': products,
        'special_offers': special_offers,
        'offer_name': offer_name,  # This will be None for the /special-offers/ path
        'current_sorting': current_sorting,  # Pass current sorting info
    }

    return render(request, 'products/special_offer_products.html', context)

