from django.contrib import admin
from .models import Invoice,Invoice_detail,Rate, Shop_details,Silver_Invoice_detail,Silver_Invoice,Product,Silver_Product,Shop_details


# Register your models here.
admin.site.register(Invoice)
admin.site.register(Invoice_detail)
admin.site.register(Rate)
admin.site.register(Silver_Invoice)
admin.site.register(Silver_Invoice_detail)
admin.site.register(Product)
admin.site.register(Silver_Product)
admin.site.register(Shop_details)


