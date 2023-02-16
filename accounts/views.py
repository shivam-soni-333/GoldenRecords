from django.shortcuts import render
from django.http.response import HttpResponse, JsonResponse
from datetime import date
from .models import Income,opening_balance,Expense
import json
from dashboard.models import Shop_details,Rate
# Create your views here.

date = date.today()
def income(request):
    global date
    #enter income to db
    if request.is_ajax():
        if request.method=="POST":
            obj = {}
            data = json.loads(request.body)
            date = data['date']
            description = data['description']
            amount = data['amount']
            try:
                income = Income(date=date,description=description,amount=amount)
                income.save()
                try:
                    balance = opening_balance.objects.get(date=date)
                    new_balance = float(balance.balance) + float(amount)
                    balance.balance = new_balance
                    balance.save()
                except Exception as e:
                    print(e)
                    balance = opening_balance.objects.last()
                    balance =float(balance.balance) + float(amount)
                    opening_balance(date=date,balance=balance).save()

                obj['success'] = "true"
            except Exception as e:
                print(e)
                obj['success'] = "false"
                obj['error'] = str(e)
            return JsonResponse(obj,safe=False)  
    #delete income from table
    if request.is_ajax():
        if request.method=="DELETE":
            obj = {}
            data = json.loads(request.body)
            id= data['id']
            try:
                to_be_delete = Income.objects.get(id=id)
                minus_balance =to_be_delete.amount
                bal =opening_balance.objects.last()
                print(bal.balance)
                bal.balance = bal.balance - minus_balance
                print(bal.balance)
                bal.save()
                to_be_delete.delete()
                obj['success'] = "true"
            except Exception as e:
                print(e)
                obj['success'] = "false"
                obj['error'] =e 
            return JsonResponse(obj,safe=False)
    
    obj = {}
    obj['date'] = str(date)
    try:
        rate = Rate.objects.get(date=date.today())
        obj['rate'] = rate
    except:
        obj['rate'] = "null"
    income = Income.objects.all()
    expense = Expense.objects.all()
    
    try:
        result= opening_balance.objects.last()
        obj['balance'] = result
    except Exception as e:
        print(e)
        obj['balance'] = "null"
    obj['income'] = income
    obj['expense'] = expense
    shop =  Shop_details.objects.last()
    if shop != None:
        obj['shop'] = shop
    else:
        obj['shop'] = "null"
    return render(request,"income.html",context=obj)

def expense(request):
    global date
    #enter income to db
    if request.is_ajax():
        if request.method=="POST":
            obj = {}
            data = json.loads(request.body)
            date = data['date']
            description = data['description']
            amount = data['amount']
            try:
                expense = Expense(date=date,description=description,amount=amount)
                expense.save()
                try:
                    balance = opening_balance.objects.get(date=date)
                    new_balance = float(balance.balance) - float(amount)
                    balance.balance = new_balance
                    balance.save()
                except Exception as e:
                    print(e)
                    balance = opening_balance.objects.last()
                    balance =float(balance.balance) - float(amount)
                    opening_balance(date=date,balance=balance).save()

                obj['success'] = "true"
            except Exception as e:
                print(e)
                obj['success'] = "false"
                obj['error'] = str(e)
            return JsonResponse(obj,safe=False)  
    
    #delete income from table
    if request.is_ajax():
        if request.method=="DELETE":
            obj = {}
            data = json.loads(request.body)
            id= data['id']
            try:
                to_be_delete = Expense.objects.get(id=id)
                plus_balance =to_be_delete.amount
                bal =opening_balance.objects.last()
                bal.balance = bal.balance + plus_balance
                bal.save()
                to_be_delete.delete()
                obj['success'] = "true"
            except Exception as e:
                print(e)
                obj['success'] = "false"
                obj['error'] =str(e)
            return JsonResponse(obj,safe=False)
    
    
