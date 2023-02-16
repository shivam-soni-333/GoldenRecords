from typing import IO
from django.http.response import HttpResponse
from django.shortcuts import redirect, render,HttpResponse
from django.contrib.auth.models import User,auth
from django.contrib import messages
from django.http import JsonResponse,HttpResponseRedirect
from dashboard.models import Invoice,Invoice_detail,Rate,Silver_Invoice,Silver_Invoice_detail,Product,Silver_Product,Shop_details
from django.template.loader import get_template
import json
from xhtml2pdf import pisa
from reportlab.pdfgen import canvas  
import math
import pdfkit
from io import BytesIO
from django.template.loader import render_to_string
from itertools import chain
from accounts.models import Income,opening_balance,Expense
from django.core.mail import send_mail
import string
from datetime import date, timedelta

def is_ajax(request):
    return request.META.get('HTTP_X_REQUESTED_WITH') == 'XMLHttpRequest'

# Create your views here.
json_data = {}
counter = 1
def index(request):
    if request.method =="POST":
        username = request.POST['username']
        password = request.POST['password']
        user  = auth.authenticate(username=username,password=password)
        if user != None:
            auth.login(request,user)
            return redirect("/dashboard")
        else:
            messages.error(request,"Wrong Username/Password")
    return render(request,'login.html')



def dashboard(request):
    obj = {}
    try:
        rate = Rate.objects.get(date=date.today())
        obj['rate'] = rate
    except:
        obj['rate'] = "null"
    try:
        obj['invoice'] = Invoice.objects.all().filter(invoice_date=date.today())
        obj['invoice'] = len(obj['invoice'])
    except Exception as e:
        print(e)
        obj['invoice'] = "null"
    try:
        obj['silver_invoice'] = Silver_Invoice.objects.all().filter(invoice_date=date.today())
        obj['silver_invoice'] = len(obj['silver_invoice'])
    except Exception as e:
        print(e)
        obj['silver_invoice'] = "null"
    try:
        obj['product'] = Product.objects.filter(is_selled="False")
        sum = 0

        for i in obj['product']:
            sum+=float(i.weight)
        
        
        obj['product'] = len(obj['product'])
        obj['product_weight'] = round(sum,2)
    except Exception as e:
        print(e)
        obj['product'] = "null"
        obj['product_weight'] = sum
   
    try:
        obj['product_22'] = Product.objects.filter(is_selled="False",carat="22K")
        sum = 0

        for i in obj['product_22']:
            sum+=float(i.weight)
        
        obj['product_22'] = len(obj['product_22'])
        obj['product_weight_22'] = round(sum,2)

    except Exception as e:
        print(e)
        obj['product_22'] = "null"
        obj['product_weight_22'] = sum

    try:
        obj['product_18'] = Product.objects.filter(is_selled="False",carat="18K")
        sum = 0

        for i in obj['product_18']:
            sum+=float(i.weight)
        
        obj['product_18'] = len(obj['product_18'])
        obj['product_weight_18'] = round(sum,2)
    except Exception as e:
        print(e)
        obj['product_18'] = "null"
        obj['product_weight_18'] = sum

    try:
        income = Income.objects.filter(date=date.today())
        sum_of_income = 0
        for i in income:
            sum_of_income+=i.amount
        print(sum_of_income)
        obj['today_income']=sum_of_income
        balance = opening_balance.objects.last()
        balance = balance.balance
        obj['balance'] = balance
        expense = Expense.objects.filter(date=date.today())
        sum_of_expense = 0
        for i in expense:
            sum_of_expense+=i.amount
        obj['expense']=sum_of_expense
    except:
        obj['today_income']="null"
        obj['expense']="null"
    
    shop =  Shop_details.objects.last()
    if shop != None:
        obj['shop'] = shop
    else:
        obj['shop'] = "null"
    return render(request,'dashboard.html',context = obj)

def logout(request):
    auth.logout(request)
    return redirect("login")

def gold(request):
    global json_data,counter
    #product_search
    if is_ajax(request):
        if request.method =="POST" and 'pid' in request.POST:
            pid = request.POST['pid']
            pid  = pid.upper()
            obj = {}
            try:
                product=Product.objects.get(pid=pid,is_selled="False")
                rate = Rate.objects.get(date=date.today())
                obj['success'] = True
                obj['product_name'] = product.name
                obj['grossweight'] = product.grossweight
                obj['weight'] = product.weight
                obj['hm_code'] = product.hm_code
                obj['labour'] = product.labour
                obj['labour_type'] = product.labour_type
                obj['carat'] = product.carat
                if obj['carat'] =="22K":
                    if obj['labour_type'] =="pergram":
                        #pergam = labour+goldrate * weight

                        temp = obj['labour'] + rate.gold_22_kt_price
                        total_this = temp*obj['weight']
                        obj['product_total'] = total_this
                        obj['gst'] = total_this*3/100
                        obj['invoice_total']=obj['gst']+total_this
                    elif obj['labour_type'] =="mrp":
                        #mrp--> (weight*gold rate)+labour
                    
                        temp = obj['weight']*rate.gold_22_kt_price
                        total_this = round(temp+obj['labour'])
                    
                        obj['product_total'] = total_this
                        obj['gst'] = total_this*3/100
                        obj['invoice_total']=obj['gst']+total_this


                elif obj['carat'] =="18K":
                    if obj['labour_type'] == "pergram" :
                        #pergram --> (gold_rate+labour)*weight

                        temp = obj['labour']  + rate.gold_18_kt_price
                        total_this = temp*obj['weight']
                        total_this = round(total_this)
                        obj['product_total'] = total_this
                        obj['gst'] = total_this*3/100
                        obj['invoice_total']=obj['gst']+total_this
                    elif obj['labour_type'] =="mrp":
                        #weight --> (gold_rate*weight)+labour

                        temp = obj['weight']*rate.gold_18_kt_price
                        total_this = round(temp+obj['labour'])
                       
                        obj['product_total'] = total_this
                        obj['gst'] = total_this*3/100
                        obj['invoice_total']=obj['gst']+total_this

            except:
                obj['success'] = False
            return JsonResponse(obj)
        

    #finalsubmit
    if is_ajax(request):
        if request.method =="POST":
            try:    
                data = json.loads(request.body)
                customer_name = data['customer_name']
                phone_no = data['phone_no']
                pan_no = data['pan_no']
                gst_no = data['gst_no']
                if pan_no == "":
                    pan_no = None
                
                
                    

                product_total = data['product_total']
                sgst = data['sgst']
                cgst = data['cgst'] 
                product_detail = data['product_detail']
                total_with_gst=data['total_with_gst']
                is_estimate = data['is_estimate']
                invoice_date = date.today()

                #insert data to db
                invo_number = Invoice.objects.last()
                invo_number = invo_number.invoice_number + 1
                
                invoice = Invoice(invoice_number = invo_number,
                invoice_date = invoice_date,
                customer_name=customer_name,
                customer_phone_number = phone_no,
                pan_number=pan_no,
                gst_number=gst_no,
                product_total = product_total,
                sgst = sgst,
                cgst = cgst,
                invoice_total = total_with_gst,is_estimate=is_estimate)

                invoice.save()
                invoice_number = invoice.invoice_number
                print(product_detail)
                for i in product_detail:
                    product_name = i['product_name']
                    hm_code = i['hm_code']
                    grossweight = i['grossweight']
                    netweight = i['weight']
                    carat = i['carat']
                    gold_rate = i['goldrate']
                    labour = i['labour']
                    total = i['total']
                    other_charge = i['other_charge']
                    
                    invoice_detail_obj = Invoice_detail(invoice_number = Invoice.objects.get(invoice_number=invoice_number),
                    product_name=product_name,
                    hm_code = hm_code,
                    grossweight = grossweight,
                    netweight=netweight,
                    carat=carat,
                    gold_rate=gold_rate,
                    labour = labour,
                    total=total,
                    other_charge=other_charge
                    )
                    invoice_detail_obj.save()
                    try:
                        product = Product.objects.get(hm_code=hm_code)
                        product.is_selled="True"
                        product.save()
                    except Exception as e:
                        print(e)
                  
                print("Data Saved!!!")
                income = Income(date=date,description="Gold Invoice Number "+str(invoice_number),amount=total_with_gst)
                income.save()
                try:
                    balance = opening_balance.objects.get(date=date.today())

                    new_balance = float(balance.balance) + float(total_with_gst)
                    balance.balance = new_balance
                    balance.save()
                except Exception as e:
                    print(e)
                    balance = opening_balance.objects.last()
                    balance =float(balance.balance) + float(total_with_gst)
                    opening_balance(date=date.today(),balance=balance).save()


                return HttpResponse(f"http://127.0.0.1:8000/generate_gold_invoice/{invoice_number}")
            except Exception as e:
                print(e)
                return HttpResponse("null")
    
    obj = {}
    try:
        obj['gold_rate'] = Rate.objects.get(date=date.today())
    except:
        obj['gold_rate'] ="null"
    try:
        rate = Rate.objects.get(date=date.today())
        obj['rate'] = rate
    except:
        obj['rate'] = "null"
    
    shop =  Shop_details.objects.last()
    if shop != None:
        obj['shop'] = shop
    else:
        obj['shop'] = "null"
    
    return render(request,"gold.html",context=obj)


def number_to_word(number):
    def get_word(n):
        words={ 0:"", 1:"One", 2:"Two", 3:"Three", 4:"Four", 5:"Five", 6:"Six", 7:"Seven", 8:"Eight", 9:"Nine", 10:"Ten", 11:"Eleven", 12:"Twelve", 13:"Thirteen", 14:"Fourteen", 15:"Fifteen", 16:"Sixteen", 17:"Seventeen", 18:"Eighteen", 19:"Nineteen", 20:"Twenty", 30:"Thirty", 40:"Forty", 50:"Fifty", 60:"Sixty", 70:"Seventy", 80:"Eighty", 90:"Ninty" }
        if n<=20:
            return words[n]
        else:
            ones=n%10
            tens=n-ones
            return words[tens]+" "+words[ones]
            
    def get_all_word(n):
        d=[100,10,100,100]
        v=["","Hundred And","Thousand","lakh"]
        w=[]
        for i,x in zip(d,v):
            t=get_word(n%i)
            if t!="":
                t+=" "+x
            w.append(t.rstrip(" "))
            n=n//i
        w.reverse()
        w=' '.join(w).strip()
        if w.endswith("And"):
            w=w[:-3]
        return w

    arr=str(number).split(".")
    number=int(arr[0])
    crore=number//10000000
    number=number%10000000
    word=""
    if crore>0:
        word+=get_all_word(crore)
        word+=" crore "
    word+=get_all_word(number).strip()+" Rupees"
    if len(arr)>1:
         if len(arr[1])==1:
            arr[1]+="0"
         word+=" and "+get_all_word(int(arr[1]))+" paisa"
    return word

def generate_gold_invoice(request,invoice_number):
    obj = {}
    try:
        invoice  = Invoice.objects.get(invoice_number=invoice_number)
      
        invoice_detail = Invoice_detail.objects.filter(invoice_number=invoice_number)
        invoice_detail_count = len(invoice_detail)
        if invoice_detail_count == 1:
            obj['invoice_detail_count'] = 1
        elif invoice_detail_count == 2:
            obj['invoice_detail_count']=2
        elif invoice_detail_count == 3:
            obj['invoice_detail_count']= 3
        elif invoice_detail_count ==4:
            obj['invoice_detail_count'] = 4
        elif invoice_detail_count == 5:
            obj['invoice_detail_count']=5
        else:
            obj['invoice_detail_count'] =  5
        shop = Shop_details.objects.last()
        obj['shop']=shop
        obj['invoice'] = invoice
        obj['invoice_detail'] = invoice_detail
        
        obj['word']=number_to_word(invoice.invoice_total)
    except:
        return HttpResponse("Invalid invoice number")
    try:
        shop=Shop_details.objects.last()
        
        if shop != None:
            obj['shop'] = shop
        else:
            obj['shop'] = "null"
    except:
        obj['shop'] = "null"
    
    #pdf = render_to_pdf('generate_gold_invoice.html', obj)    
    # return HttpResponse(pdf, content_type='application/pdf')
    return render(request,"generate_gold_invoice.html",obj)
   
def generate_silver_invoice(request,invoice_number):
    try:
        silver_invoice = Silver_Invoice.objects.get(invoice_number=invoice_number)
        
        silver_invoice_detail = Silver_Invoice_detail.objects.filter(invoice_number=invoice_number)
    except Exception as e:
        print(e)
        return HttpResponse("Invalid invoice number")
    
    obj = {"invoice":silver_invoice,"invoice_detail":silver_invoice_detail}
    invoice_detail_count = len(silver_invoice_detail)
    print(invoice_detail_count)
    if invoice_detail_count == 1:
        obj['invoice_detail_count'] = 1
    elif invoice_detail_count == 2:
        obj['invoice_detail_count']=2
    elif invoice_detail_count == 3:
        obj['invoice_detail_count']= 3
    elif invoice_detail_count ==4:
        obj['invoice_detail_count'] = 4
    elif invoice_detail_count == 5:
        obj['invoice_detail_count']=5
    else:
        obj['invoice_detail_count'] =  5

        
    try:
        shop=Shop_details.objects.last()
        print(shop)
        if shop != None:
            obj['shop'] = shop
        else:
            obj['shop'] = "null"
    except:
        obj['shop'] = "null"
    obj['word']=number_to_word(silver_invoice.invoice_total)
    return render(request,"generate_silver_invoice.html",obj)
def render_to_pdf(template_src, context_dict={}):
    template = get_template(template_src)
    html  = template.render(context_dict)
    result = BytesIO()
    pdf = pisa.pisaDocument(BytesIO(html.encode("ISO-8859-1")), result)
    if not pdf.err:
        return HttpResponse(result.getvalue(), content_type='application/pdf')
    return None

from datetime import date
date = date.today()

def silver(request):
    global date 
    #product search
    if is_ajax(request):
        if request.method =="POST" and 'pid' in request.POST:
            pid = request.POST['pid']
            obj = {}
            try:
                product=Silver_Product.objects.get(id=pid)
                rate = Rate.objects.get(date=date.today())
                obj['success'] = True
                obj['product_name'] = product.name
                obj['weight'] = product.weight
                obj['labour'] = product.labour
                obj['labour_type'] = product.labour_type
                
                if obj['labour_type'] =="pergram":
                    #pergam = labour+goldrate * weight

                    temp = obj['labour'] + rate.silver_1gm_price
                    total_this = temp*obj['weight']
                    obj['product_total'] = total_this
                    obj['gst'] = total_this*3/100
                    obj['invoice_total']=obj['gst']+total_this
                elif obj['labour_type'] =="mrp":
                    #mrp--> (weight*gold rate)+labour
                
                    temp = obj['weight']*rate.silver_1gm_price
                    total_this = round(temp+obj['labour'])
                
                    obj['product_total'] = total_this
                    obj['gst'] = total_this*3/100
                    obj['invoice_total']=obj['gst']+total_this

            except Exception as e:
                print(e)
                obj['success'] = False
            return JsonResponse(obj)


    #add product to table finalsubmit
    if is_ajax(request):
        if request.method =="POST":
            try:
                data = json.loads(request.body)
              
                customer_name = data['customer_name']
                phone_no = data['phone_no']
                pan_number = data['pan_no']
                gst_number = data['gst_no']
                if pan_number == "":
                    pan_number = None
                   
                        


                total_with_gst = data['total_with_gst']
                product_total = data['product_total']
                sgst = data['sgst']
                cgst = data['cgst']
                is_estimate = data['is_estimate']
                print(is_estimate)
                product_detail = data['product_detail']
                
                silv_number = Silver_Invoice.objects.last()
                silv_number = silv_number.invoice_number + 1
                
                silver_invoice = Silver_Invoice(invoice_number = silv_number,
                invoice_date=date,
                customer_name=customer_name,
                customer_phone_number = phone_no,
                pan_number=pan_number,
                gst_number=gst_number,
                    product_total=product_total,
                    sgst = sgst,
                    cgst = cgst,
                    invoice_total=total_with_gst,is_estimate=is_estimate)
                silver_invoice.save()

                invoice_number = silver_invoice.invoice_number
                for i in product_detail:
                    product_name = i['product_name']
                    weight = i['weight']
                    silver_rate = i['silverrate']
                    total = i['total']

                    silver_invoice_detail_obj = Silver_Invoice_detail(invoice_number =Silver_Invoice.objects.get(invoice_number=invoice_number),
                    product_name=product_name,
                    weight = weight,
                    silver_rate=silver_rate,
                    total=total
                    )
                    silver_invoice_detail_obj.save()

                income = Income(date=date,description="Silver Invoice Number "+str(invoice_number),amount=total_with_gst)
                income.save()
                try:
                    balance = opening_balance.objects.get(date=date.today())
                    new_balance = float(balance.balance) + float(total_with_gst)
                    balance.balance = new_balance
                    balance.save()
                except Exception as e:
                    print(e)
                    balance = opening_balance.objects.last()
                    balance =float(balance.balance) + float(total_with_gst)
                    opening_balance(date=date.today(),balance=balance).save()

            
                return HttpResponse(f"http://127.0.0.1:8000/generate_silver_invoice/{invoice_number}")
            except Exception as e:
                print(e)
                return HttpResponse("null")
            
            
    
    obj = {}
    try:
        obj['rate'] = Rate.objects.get(date=date.today())
    except:
        obj['rate'] = "null"
    shop =  Shop_details.objects.last()
    if shop != None:
        obj['shop'] = shop
    else:
        obj['shop'] = "null"
    return render(request,"silver.html",context=obj)



                

def gold_invoice(request):
    if is_ajax(request):
        if request.method=="POST":
            obj  = {}
            data = json.loads(request.body)
            search_term = data['search'] 
            invoice  = Invoice.objects.filter(invoice_number__istartswith=search_term)| Invoice.objects.filter(invoice_date__istartswith = search_term)| Invoice.objects.filter(invoice_total__istartswith=search_term) | Invoice.objects.filter(customer_name__istartswith=search_term) | Invoice.objects.filter(customer_phone_number__istartswith=search_term)
            out = []
            for i in invoice:
                temp_dict  = {}
                temp_dict['invoice_number'] = i.invoice_number
                temp_dict['invoice_date'] = i.invoice_date
                temp_dict['customer_name'] = i.customer_name
                temp_dict['customer_phone_number'] = i.customer_phone_number
                temp_dict['invoice_total'] = i.invoice_total
                out.append(temp_dict)
            
            data=out
          
            return JsonResponse(data,safe=False)

            
    obj = {}
    try:
        rate = Rate.objects.get(date=date.today())
        obj['rate'] = rate
    except:
        obj['rate'] = "null"
    
    try:
        obj['invoice'] = Invoice.objects.all().order_by('-invoice_date')
    except:
        obj['invoice'] = "null"
    shop =  Shop_details.objects.last()
    if shop != None:
        obj['shop'] = shop
    else:
        obj['shop'] = "null"
    return render(request,"goldinvoice.html",context=obj)

def silver_invoice(request):
    if is_ajax(request):
        if request.method=="POST":
            obj  = {}
            data = json.loads(request.body)
            search_term = data['search'] 
            invoice  = Silver_Invoice.objects.filter(invoice_number__istartswith=search_term)| Silver_Invoice.objects.filter(invoice_date__istartswith = search_term)| Silver_Invoice.objects.filter(invoice_total__istartswith=search_term) | Silver_Invoice.objects.filter(customer_name__istartswith=search_term) | Silver_Invoice.objects.filter(customer_phone_number__istartswith=search_term)
            out = []
            for i in invoice:
                temp_dict  = {}
                temp_dict['invoice_number'] = i.invoice_number
                temp_dict['invoice_date'] = i.invoice_date
                temp_dict['customer_name'] = i.customer_name
                temp_dict['customer_phone_number'] = i.customer_phone_number
                temp_dict['invoice_total'] = i.invoice_total
                out.append(temp_dict)
            
            data=out
          
            return JsonResponse(data,safe=False)

            
    obj = {}
    try:
        obj['invoice'] = Silver_Invoice.objects.all().order_by('-invoice_date')
    except:
        obj['invoice'] = "null"
    shop =  Shop_details.objects.last()
    if shop != None:
        obj['shop'] = shop
    else:
        obj['shop'] = "null"
    try:
        rate = Rate.objects.get(date=date.today())
        obj['rate'] = rate
    except:
        obj['rate'] = "null"
    
    return render(request,"silverinvoice.html",context=obj)
    

from datetime import date
date = date.today()
def rate(request):
    global date
    if is_ajax(request):
        if request.method=="POST":
            data =json.loads(request.body)
            
            gold_biskit_price=data['biskit_price']
            gold_22_kt_price  = data['gold_22_kt_price']
            gold_18_kt_price = data['gold_18_kt_price']
            silver_1kg_price = data['silver_1kg_price']
            silver_1gm_price = data['silver_per_gm_price']
            try:
                rate =Rate.objects.get(date = date)
               
                rate.gold_biskit_price = gold_biskit_price
                rate.gold_22_kt_price = gold_22_kt_price
                rate.gold_18_kt_price  = gold_18_kt_price
                rate.silver_1kg_price = silver_1kg_price
                rate.silver_1gm_price = silver_1gm_price
                rate.save()
                return HttpResponse("Updated value")

            except:
                # create record 
                rate = Rate(
                    date=date,
                    gold_biskit_price=gold_biskit_price,
                    gold_22_kt_price=gold_22_kt_price,
                    gold_18_kt_price = gold_18_kt_price,
                    silver_1kg_price = silver_1kg_price,
                    silver_1gm_price=silver_1gm_price
                )
                rate.save()
                print("data saved!!")
                return HttpResponse("datasaved")
    obj = {} 
    try:
        rate = Rate.objects.get(date=date)
        obj['rate'] = rate
    except:
        obj['rate'] = "null"
    shop =  Shop_details.objects.last()
    if shop != None:
        obj['shop'] = shop
    else:
        obj['shop'] = "null"
    return render(request,"rate.html",context=obj)

def product(request):
    if request.method =="POST":

        obj  = {}
        data = request.POST['search_term']
        
        search_term = data
        product = Product.objects.filter(pid__istartswith=search_term,is_selled=False)|Product.objects.filter(name__istartswith=search_term,is_selled=False)|Product.objects.filter(grossweight__istartswith=search_term,is_selled=False)|Product.objects.filter(weight__istartswith=search_term,is_selled=False)|Product.objects.filter(hm_code__istartswith=search_term,is_selled=False)
        obj = {}
        shop =  Shop_details.objects.last()
        if shop != None:
            obj['shop'] = shop
        else:
            obj['shop'] = "null"

        try:
            rate = Rate.objects.get(date=date.today())
            obj['rate'] = rate
        except:
            obj['rate'] = "null"
        #LOGIC OF COUNT AND WEIGHT 
        weight  = 0
        for i in product:
            weight += i.weight
        weight = round(weight,2)
        if len(product):
            obj['product'] = product
            obj['search_term'] = search_term
            obj['count'] = len(product)
            obj['weight'] = weight
        else:
            obj['product'] = Product.objects.filter()
            obj['error'] = 1
        return render(request,"product.html",context=obj)

    if is_ajax(request):
        if request.method =="POST":
            obj = {}
            data = json.loads(request.body)
            print(data)

    product = Product.objects.filter(is_selled=False)
    obj = {}
    obj['product'] = product
    shop =  Shop_details.objects.last()
    if shop != None:
        obj['shop'] = shop
    else:
        obj['shop'] = "null"

    try:
        rate = Rate.objects.get(date=date.today())
        obj['rate'] = rate
    except:
        obj['rate'] = "null"
    
    return render(request,"product.html",context=obj)


def autocomplete_pid(request):
    pid = request.GET['term']
    pid = pid.upper()
    pro = Product.objects.filter(pid__istartswith=pid,is_selled=False)
    out = []
    for i in pro:
        out.append(i.pid)
    return JsonResponse(out,safe=False)
def sold(request):
    if request.method =="POST":
        obj  = {}
        data = request.POST['search_term']
        
        search_term = data
        product = Product.objects.filter(pid__istartswith=search_term,is_selled=True)|Product.objects.filter(name__istartswith=search_term,is_selled=True)|Product.objects.filter(grossweight__istartswith=search_term,is_selled=True)|Product.objects.filter(weight__istartswith=search_term,is_selled=True)|Product.objects.filter(hm_code__istartswith=search_term,is_selled=True)
        obj = {}
        shop =  Shop_details.objects.last()
        if shop != None:
            obj['shop'] = shop
        else:
            obj['shop'] = "null"
        try:
            rate = Rate.objects.get(date=date.today())
            obj['rate'] = rate
        except:
            obj['rate'] = "null"
        #LOGIC OF COUNT AND WEIGHT 
        weight  = 0
        for i in product:
            weight += i.weight
        weight = round(weight,2)
        if len(product):
            obj['product'] = product
            obj['search_term'] = search_term
            obj['count'] = len(product)
            obj['weight'] = weight
        else:
            obj['product'] = Product.objects.filter()
            obj['error'] = 1
        return render(request,"product.html",context=obj)
    obj = {}
    product = Product.objects.filter(is_selled =True)
    obj['count'] = len(product)
    weight = 0.0
    for i in product:
        weight+=i.weight
    obj['weight'] = round(weight,2)
    shop =  Shop_details.objects.last()
    if shop != None:
        obj['shop'] = shop
    else:
        obj['shop'] = "null"
    try:
        rate = Rate.objects.get(date=date.today())
        obj['rate'] = rate
    except:
        obj['rate'] = "null"
            
    obj['product'] = product
    return render(request,"sold.html",context=obj)


def huid(request):
    if request.method == 'POST':
        obj = {}
        search_term = request.POST['search_term']
        product = Product.objects.filter(pid__istartswith=search_term,is_selled=False)|Product.objects.filter(name__istartswith=search_term,is_selled=False)|Product.objects.filter(grossweight__istartswith=search_term,is_selled=False)|Product.objects.filter(weight__istartswith=search_term,is_selled=False)|Product.objects.filter(hm_code__istartswith=search_term,is_selled=False)

        huid_product = []
        
        weight=0
        for i in product:
            if not i.hm_code.startswith('4DIGIT'):
                weight+=i.weight
                huid_product.append(i)

        obj = {}
        obj['search_term'] = search_term
        obj['product'] = huid_product
        obj['count'] = len(huid_product)
        obj['weight'] = round(weight,2)

        return render(request,'huid.html',context=obj)


    product = Product.objects.filter(is_selled=False,)
    huid_product = []
    weight=0
    for i in product:
        if not i.hm_code.startswith('4DIGIT'):
            weight+=i.weight
            huid_product.append(i)

    obj = {}
    obj['product'] = huid_product
    obj['count'] = len(huid_product)
    obj['weight'] = round(weight,2)
    shop =  Shop_details.objects.last()
    if shop != None:
        obj['shop'] = shop
    else:
        obj['shop'] = "null"

    try:
        rate = Rate.objects.get(date=date.today())
        obj['rate'] = rate
    except:
        obj['rate'] = "null"

    return render(request,'huid.html',context=obj)

def pid(request):
    obj = {}
    shop =  Shop_details.objects.last()
    if shop != None:
        obj['shop'] = shop
    else:
        obj['shop'] = "null"

    try:
        rate = Rate.objects.get(date=date.today())
        obj['rate'] = rate
    except:
        obj['rate'] = "null"
    
    if request.method =='POST':    
        data = request.POST['search_term']
        data = data.upper()
        lst_a_to_z = []
        for i in string.ascii_uppercase:
            lst_a_to_z.append(i)
        
        range_post = request.POST['range']
        pos = range_post.find('-')
        start = range_post[:pos]
        end = range_post[pos+1:]

        if not start.isdigit() and not end.isdigit():
            obj['error'] = True
            obj['data'] = False
            return render(request,'pid.html',context=obj)
            
             
        
        if data in lst_a_to_z:
            free_pid = []
            for i in range(int(start),int(end)):
                id = str(data)+str(i)
                product = Product.objects.filter(pid=id)
                if len(product) == 0:
                    free_pid.append(id)
            obj['data'] = free_pid
            obj['error'] = False
            return render(request,'pid.html',context=obj)

        else:
            obj['error'] = True
            obj['data'] = False
            return render(request,'pid.html',context=obj)
        


    return render(request,'pid.html',context=obj)

def one_month_statement(request):
    
    if request.method == "POST":
        start_date = request.POST['start_date']
        end_date = request.POST['end_date']
        if start_date <= end_date and start_date !="" or end_date!="":
            obj = {}
            invoice = Invoice.objects.filter(invoice_date__range=[start_date,end_date])
            c = 0
            for i in invoice:
                obj[str(c)] = {}
                obj[str(c)]['invoice'] ={}
                
                obj[str(c)]['invoice']['invoice_number'] = i.invoice_number
                obj[str(c)]['invoice']['invoice_date'] = i.invoice_date
                obj[str(c)]['invoice']['customer_name'] = i.customer_name
                obj[str(c)]['invoice']['customer_phone_number'] = i.customer_phone_number
                
                if i.pan_number != None:
                    obj[str(c)]['invoice']['pan_number'] = i.pan_number
                else:
                    obj[str(c)]['invoice']['pan_number'] =""
                
                if i.gst_number != None:
                    obj[str(c)]['invoice']['gst_number'] = i.gst_number
                else:
                    obj[str(c)]['invoice']['gst_number'] = ""
                

                obj[str(c)]['invoice']['pro_total'] = i.product_total
                obj[str(c)]['invoice']['sgst'] = i.sgst
                obj[str(c)]['invoice']['cgst'] = i.cgst
                obj[str(c)]['invoice']['invoice_total'] = i.invoice_total


                #invoice_detail
                invoice_detail = Invoice_detail.objects.filter(invoice_number = i.invoice_number)
                obj[str(c)]['invoice_detail'] = {}
                # obj[str(c)]['invoice_detail']['invoice_number'] =invoice_detail.invoice_number 
                coun  = 0
                for invo in invoice_detail:
                    obj[str(c)]['invoice_detail'][str(coun)] = {}
                    
                    obj[str(c)]['invoice_detail'][str(coun)]['product_name'] =invo.product_name 
                    obj[str(c)]['invoice_detail'][str(coun)]['hm_code'] =invo.hm_code
                    obj[str(c)]['invoice_detail'][str(coun)]['grossweight'] =invo.grossweight
                    obj[str(c)]['invoice_detail'][str(coun)]['weight'] =invo.netweight
                    obj[str(c)]['invoice_detail'][str(coun)]['carat'] =invo.carat
                    obj[str(c)]['invoice_detail'][str(coun)]['gold_rate'] =invo.gold_rate
                    obj[str(c)]['invoice_detail'][str(coun)]['labour'] =invo.labour
                    obj[str(c)]['invoice_detail'][str(coun)]['total'] =invo.total
                    obj[str(c)]['invoice_detail'][str(coun)]['other_charge'] =invo.other_charge
                    coun +=1
                                
                c+=1
            data ={}  
            data['data'] = obj
            data['start_date'] = start_date
            data['end_date'] = end_date
            return render(request,'one_month_gold_invoice.html',context=data)
        else:
            obj= {}
            obj['data'] = ""
            obj['error'] = True
            return render(request,'one_month_gold_invoice.html',context=obj)

        
    #get request
    obj={}

    end_date= date.today().replace(day=1) - timedelta(days=1)

    start_date = date.today().replace(day=1) - timedelta(days=end_date.day)
   
    obj['st_date']  = str(start_date)
    obj['end_date'] = str(end_date)
    return render(request,'one_month_gold_invoice.html',context=obj)

def one_month_silver_statement(request):
    if request.method=="POST":
        start_date = request.POST['start_date']
        end_date = request.POST['end_date']
        if end_date > start_date  or( start_date !="" or end_date!="" ):
            obj = {}
            obj['start_date'] = start_date
            obj['end_date'] = end_date

            silver_invoice = Silver_Invoice.objects.filter(invoice_date__range=[start_date,end_date])
            c=0
            data ={}
            for i in silver_invoice:
                
                data[str(c)] = {}
                data[str(c)]['invoice'] = {}

                data[str(c)]['invoice']['invoice_number'] = i.invoice_number
                data[str(c)]['invoice']['invoice_date'] = i.invoice_date
                data[str(c)]['invoice']['customer_name'] = i.customer_name
                data[str(c)]['invoice']['customer_phone_number'] = i.customer_phone_number
                
                if i.pan_number != None:
                    data[str(c)]['invoice']['pan_number'] = i.pan_number
                else:
                    data[str(c)]['invoice']['pan_number'] =""
                
                if i.gst_number != None:
                    data[str(c)]['invoice']['gst_number'] = i.gst_number
                else:
                    data[str(c)]['invoice']['gst_number'] = ""
                

                data[str(c)]['invoice']['pro_total'] = i.product_total
                data[str(c)]['invoice']['sgst'] = i.sgst
                data[str(c)]['invoice']['cgst'] = i.cgst
                data[str(c)]['invoice']['invoice_total'] = i.invoice_total

                #silver_invoice_detail
                invoice_detail = Silver_Invoice_detail.objects.filter(invoice_number = i.invoice_number)
                data[str(c)]['invoice_detail'] = {}
                # obj[str(c)]['invoice_detail']['invoice_number'] =invoice_detail.invoice_number 
                coun  = 0
                for invo in invoice_detail:
                    data[str(c)]['invoice_detail'][str(coun)] = {}
                    
                    data[str(c)]['invoice_detail'][str(coun)]['product_name'] =invo.product_name 
                    data[str(c)]['invoice_detail'][str(coun)]['weight'] =invo.weight
                    data[str(c)]['invoice_detail'][str(coun)]['silver_rate'] =invo.silver_rate
                    data[str(c)]['invoice_detail'][str(coun)]['total'] =invo.total
                    coun +=1
                                
                c+=1
                

            obj['data'] = data
            return render(request,'one_month_silver_invoice.html',context=obj)
        else:
            obj={}
            obj['data'] = ""
            obj['error'] = True
            print("error")
            return render(request,'one_month_silver_invoice.html',context=obj)

    obj={}

    end_date= date.today().replace(day=1) - timedelta(days=1)

    start_date = date.today().replace(day=1) - timedelta(days=end_date.day)
   
    obj['st_date']  = str(start_date)
    obj['end_date'] = str(end_date)
    
    return render(request,'one_month_silver_invoice.html',context=obj)