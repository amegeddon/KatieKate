from django.shortcuts import render, redirect, reverse, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from .models import Product, Category, SpecialOffer
from django.db.models.functions import Lower
from .forms import ProductForm


# Create your views here.


def all_products(request):
    """
    A view to show all products, including sorting and search queries.

    This view handles displaying all products with options for sorting by name
    or category, filtering by categories, and performing a search query on
    product names or descriptions.
    """
    products = Product.objects.all()
    categories = None
    query = None
    sort = None
    direction = None

    if request.GET:
        # Handle sorting
        if "sort" in request.GET:
            sortkey = request.GET["sort"]
            sort = sortkey
            if sortkey == "name":
                sortkey = "lower_name"
                products = products.annotate(lower_name=Lower("name"))

            if sortkey == "category":
                sortkey = "category__name"

            if "direction" in request.GET:
                direction = request.GET["direction"]
                if direction == "desc":
                    sortkey = f"-{sortkey}"
            products = products.order_by(sortkey)

        # Handle filtering by category
        if "category" in request.GET:
            categories = request.GET["category"].split(",")
            products = products.filter(category__name__in=categories)
            categories = Category.objects.filter(name__in=categories)

        # Handle search query
        if "q" in request.GET:
            query = request.GET["q"]
            if not query:
                messages.error(
                    request, "You didn't enter any search criteria!"
                )
                return redirect(reverse("products"))
            queries = Q(name__icontains=query) | Q(
                description__icontains=query
            )
            products = products.filter(queries)

    current_sorting = f"{sort}_{direction}"

    # Fetch all categories by default if `categories` is None after /
    # processing GET parameters
    if categories is None:
        categories = Category.objects.all()

    context = {
        "products": products,
        "search_term": query,
        "current_categories": categories,
        "current_sorting": current_sorting,
    }

    return render(request, "products/products.html", context)


def product_detail(request, product_id):
    """
    A view to show individual product details.

    This view handles the display of a single product's details based on
    the product ID.
    """
    product = get_object_or_404(Product, pk=product_id)

    context = {
        "product": product,
    }

    return render(request, "products/product_detail.html", context)


@login_required
def add_product(request):
    """
    Add a product to the store.

    This view allows store owners to add new products to the store. It requires
    the user to be logged in and have store owner (superuser) permissions.
    """
    if not request.user.is_superuser:
        messages.error(request, "Sorry, only store owners can do that.")
        return redirect(reverse("home"))

    if request.method == "POST":
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            product = form.save()
            messages.success(request, "Successfully added product!")
            return redirect(reverse("product_detail", args=[product.id]))
        else:
            messages.error(
                request,
                "Failed to add product. Please ensure the form is valid.",
            )
    else:
        form = ProductForm()

    template = "products/add_product.html"
    context = {
        "form": form,
    }

    return render(request, template, context)


@login_required
def edit_product(request, product_id):
    """
    Edit a product in the store.

    This view allows store owners to edit an existing product. It requires
    the user to be logged in and have store owner (superuser) permissions.
    """
    if not request.user.is_superuser:
        messages.error(request, "Sorry, only store owners can do that.")
        return redirect(reverse("home"))

    product = get_object_or_404(Product, pk=product_id)
    if request.method == "POST":
        form = ProductForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            form.save()
            messages.success(request, "Successfully updated product!")
            return redirect(reverse("product_detail", args=[product.id]))
        else:
            messages.error(
                request,
                "Failed to update product. Please ensure the form is valid.",
            )
    else:
        form = ProductForm(instance=product)
        messages.info(request, f"You are editing {product.name}")

    template = "products/edit_product.html"
    context = {
        "form": form,
        "product": product,
    }

    return render(request, template, context)


@login_required
def delete_product(request, product_id):
    """
    Delete a product from the store.

    This view allows store owners to delete a product from the store./
    It requires the user to be logged in and have store owner (superuser)/
    permissions.
    """
    if not request.user.is_superuser:
        messages.error(request, "Sorry, only store owners can do that.")
        return redirect(reverse("home"))

    product = get_object_or_404(Product, pk=product_id)
    product.delete()
    messages.success(request, "Product deleted!")
    return redirect(reverse("products"))


def special_offer_products(request, offer_name=None):
    """
    A view to filter products by special offers (e.g., new_arrivals, /
    deals, clearance) and allow sorting.

    This view displays products associated with special offers, with options
    for filtering by category, search queries, and sorting.
    """
    products = Product.objects.filter(special_offer__isnull=False)

    if offer_name:
        special_offer = SpecialOffer.objects.filter(name=offer_name).first()

        if special_offer:
            products = products.filter(special_offer=special_offer)
        else:
            products = (
                Product.objects.none()
            )  # If no offer matches, show no products

    categories = None
    query = None
    sort = None
    direction = "asc"  # Default sorting direction is ascending
    sortkey = "name"  # Default sort key is by name

    if request.GET:
        # Handle sorting by different criteria
        if "sort" in request.GET:
            sortkey = request.GET["sort"]
            sort = sortkey

            if sortkey == "name":
                sortkey = "lower_name"
                products = products.annotate(lower_name=Lower("name"))

            if sortkey == "category":
                sortkey = "category__name"

            if "direction" in request.GET:
                direction = request.GET["direction"]
                if direction == "desc":
                    sortkey = f"-{sortkey}"

        # Handle filtering by category
        if "category" in request.GET:
            categories = request.GET["category"].split(",")
            products = products.filter(category__name__in=categories)
            categories = Category.objects.filter(name__in=categories)

        # Handle search query
        if "q" in request.GET:
            query = request.GET["q"]
            if not query:
                messages.error(
                    request, "You didn't enter any search criteria!"
                )
                return redirect(
                    reverse("special_offer_products", args=[offer_name])
                )
            queries = Q(name__icontains=query) | Q(
                description__icontains=query
            )
            products = products.filter(queries)

    products = products.order_by(sortkey)

    special_offers = SpecialOffer.objects.all()

    current_sorting = f"{sort}_{direction}"

    if categories is None:
        categories = Category.objects.all()

    context = {
        "products": products,
        "special_offers": special_offers,
        "offer_name": offer_name,
        "current_sorting": current_sorting,
        "search_term": query,
        "current_categories": categories,
    }

    return render(request, "products/special_offer_products.html", context)
