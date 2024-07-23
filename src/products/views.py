from django.shortcuts import render

# Create your views here.
import mimetypes

from django.http import HttpResponseRedirect, HttpResponseBadRequest,FileResponse
from django.shortcuts import render, redirect, get_object_or_404
# from cfehome.storages.utils import generate_presigned_url
# Create your views here.
from .forms import ProductForm, ProductUpdateForm, ProductAttachmentInlineFormSet
from .models import Product, ProductAttachment


def product_create_view(request):
    context = {}
    form = ProductUpdateForm(request.POST or None)
    if form.is_valid():
        obj = form.save(commit=False)
        if request.user.is_authenticated:
            obj.user = request.user
            obj.save()
            return redirect(obj.get_manage_url())
        form.add_error(None, "Your must be logged in to create products.")
    context['form'] = form
    return render(request, 'products/create.html', context)

def product_list_view(request):
    object_list = Product.objects.all()
    return render(request, "products/list.html", {"object_list": object_list})





def product_manage_detail_view(request, handle=None):
    obj = get_object_or_404(Product, handle=handle)
    attachments = ProductAttachment.objects.filter(product=obj)
    is_manager = request.user.is_authenticated and obj.user == request.user
    
    if not is_manager:
        return HttpResponseBadRequest("You are not authorized to manage this product.")
    
    form = ProductUpdateForm(request.POST or None, request.FILES or None, instance=obj)
    formset = ProductAttachmentInlineFormSet(request.POST or None, 
                                             request.FILES or None, queryset=attachments)
    
    if form.is_valid() and formset.is_valid():
        instance = form.save(commit=False)
        instance.save()
        for _form in formset:
            attachment_obj = _form.save(commit=False)
            if _form.cleaned_data.get("DELETE"):
                if attachment_obj.pk:
                    attachment_obj.delete()
            else:
                attachment_obj.product = instance
                attachment_obj.save()
        return redirect(obj.get_manage_url())
    
    context = {
        'object': obj,
        'form': form,
        'formset': formset,
    }
    return render(request, 'products/manager.html', context)


def product_detail_view(request, handle=None):
    obj = get_object_or_404(Product, handle=handle)
    attachments = ProductAttachment.objects.filter(product=obj)
    # attachments = obj.productattachment_set.all()
    is_owner = False
    if request.user.is_authenticated:
        is_owner = request.user.purchase_set.all().filter(product=obj, completed=True).exists()
    context = {"object": obj, "is_owner": is_owner, "attachments": attachments}
    return render(request, 'products/detail.html', context)

def product_attachment_download_view(request, handle=None, pk=None):
    # Retrieve the product attachment object
    attachment = get_object_or_404(ProductAttachment, product__handle=handle, pk=pk)

    # Check if the attachment is free or if the user is authenticated
    can_download = attachment.is_free or False
    if request.user.is_authenticated:
        can_download = True
        # Uncomment and adjust the following line if you have purchase verification logic
        # can_download = request.user.purchase_set.all().filter(product=attachment.product, completed=True).exists()

    # If the user cannot download, return a bad request response
    if not can_download:
        return HttpResponseBadRequest()

    # Open the attachment file in binary read mode
    file = attachment.file.open(mode='rb') # Assuming S3 object storage
    filename = attachment.file.name

    # Determine the MIME type of the file
    content_type, _ = mimetypes.guess_type(filename)

    # Create a FileResponse to send the file to the client
    response = FileResponse(file)
    response['Content-Type'] = content_type or 'application/octet-stream'
    response['Content-Disposition'] = f'attachment; filename={filename}'

    return response