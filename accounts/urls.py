from django.contrib import admin
from django.urls import path,include
from accounts import views
urlpatterns = [
    path('income',views.income,name="income"),
    path('expense',views.expense,name="expense")
]