from django.db import models


# Create your models here.
class Invoice(models.Model):
    # invoice number,invoice_date,customer_name,customer_phone_number,pan_number,total,
    invoice_number = models.IntegerField(primary_key=True,editable=False)
    invoice_date = models.DateField()
    customer_name = models.CharField(max_length=100)
    customer_phone_number=models.CharField(max_length=10,blank=True)
    pan_number = models.CharField(max_length=100,default=None,blank=True,null=True)
    gst_number = models.CharField(max_length=100,default=None,blank=True,null=True)
    product_total = models.FloatField()
    sgst = models.FloatField()
    cgst = models.FloatField()
    invoice_total = models.FloatField()
    is_estimate = models.CharField(max_length=5)
    
    def __str__(self):
        return str(str(self.invoice_number)+" "+self.customer_name)


class Invoice_detail(models.Model):
    #id,invoice_number(forieng key),product_name,weight,carat,gold_Rate,total
    invoice_number  = models.ForeignKey(Invoice,on_delete=models.CASCADE)
    product_name  = models.CharField(max_length= 100)
    hm_code = models.CharField(max_length=100)
    grossweight=models.FloatField()
    netweight = models.FloatField()
    carat = models.CharField(max_length=10)
    gold_rate = models.CharField(max_length=100)
    labour = models.CharField(max_length=10)
    total = models.FloatField()
    other_charge = models.FloatField(default=0)

    def __str__(self):
        return str(str(self.invoice_number)+" "+self.product_name)

class Rate(models.Model):
    date = models.DateField(primary_key=True)
    gold_biskit_price = models.FloatField()
    gold_22_kt_price = models.FloatField()
    gold_18_kt_price = models.FloatField()
    silver_1kg_price = models.FloatField()
    silver_1gm_price  = models.FloatField()

class Silver_Invoice(models.Model):
    invoice_number = models.IntegerField(primary_key=True,editable=False)
    invoice_date = models.DateField()
    customer_name = models.CharField(max_length=100)
    customer_phone_number=models.CharField(max_length=10,blank=True)
    pan_number = models.CharField(max_length=100,default=None,blank=True,null=True)
    gst_number = models.CharField(max_length=100,default=None,blank=True,null=True)
    product_total = models.FloatField()
    sgst = models.FloatField()
    cgst = models.FloatField()
    invoice_total = models.FloatField()
    is_estimate = models.CharField(max_length=5)

    def __str__(self):
        return str(str(self.invoice_number)+" "+self.customer_name)

class Silver_Invoice_detail(models.Model):
    #id,invoice_number(forieng key),product_name,weight,carat,gold_Rate,total
    invoice_number  = models.ForeignKey(Silver_Invoice,on_delete=models.CASCADE)
    product_name  = models.CharField(max_length= 100)
    weight = models.FloatField()
    silver_rate = models.CharField(max_length=100)
    total = models.FloatField()

    def __str__(self):
        return str(str(self.invoice_number)+" "+self.product_name)

class Product(models.Model):
    pid = models.CharField(max_length=100,primary_key=True)
    name = models.CharField(max_length=100)
    grossweight = models.FloatField()
    weight = models.FloatField()
    hm_code = models.CharField(max_length=100,blank=True,unique=True)
    labour = models.IntegerField()
    is_selled = models.CharField(max_length=5,choices=(('False','False'),('True','True')),default='False')
    supplier = models.CharField(max_length=1000,blank=True)
    #carat have two choices--> 22K and 18K
    carat_choice = (
        ('22K','22K'),
        ('18K','18K')
        )
    carat = models.CharField(max_length=3,choices=carat_choice)
    
    #labour_type have two choices --> pergram and mrp
    labour_choice = (
        ('pergram','pergram'),
        ('mrp','mrp')
    )
    labour_type = models.CharField(max_length=7,choices=labour_choice)

    def __str__(self):
        return (self.name+" "+str(self.pid))
    def save(self, *args, **kwargs):
        try:
            desc = Product.objects.get(hm_code=self.hm_code)
            desc.update(pid=self.pid,name=self.name,grossweight=self.grossweight,weight=self.weight,hm_code=self.hm_code,labour=self.labour,is_selled=self.is_selled)
        except:
            if self.hm_code =="":
                self.hm_code = "4DIGIT"+str(self.pid)
            super(Product, self).save(*args, **kwargs)
            print("in update")
            
                
    
   

class Silver_Product(models.Model):
    name  = models.CharField(max_length=100)
    weight = models.FloatField()
    labour = models.IntegerField()
    labour_choice = (
        ('pergram','pergram'),
        ('mrp','mrp')
    )
    labour_type = models.CharField(max_length=7,choices=labour_choice)


class Shop_details(models.Model):
    name = models.CharField(max_length=100)
    address = models.CharField(max_length=200)
    phone_number = models.CharField(max_length=10,blank=True)
    phone_number_2 = models.CharField(max_length=10,blank=True)
    gst_number = models.CharField(max_length=100)
    bis_hm_number = models.CharField(max_length=100)

    def __str__(self):
        return (str(self.name))
