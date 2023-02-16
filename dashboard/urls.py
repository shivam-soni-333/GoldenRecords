from django.contrib import admin
from django.urls import path,include
from dashboard import views
from django.contrib.auth import views as auth_views
urlpatterns = [
    path('',views.index,name='login'),
    path('password_reset',auth_views.PasswordResetView.as_view(),name='password_reset'),
    path('password_reset/done',auth_views.PasswordResetDoneView.as_view(),name="password_reset_done"),
    path('reset/<uidb64>/<token>/',auth_views.PasswordResetConfirmView.as_view(),name="password_reset_confirm"),
    path('reset/done',auth_views.PasswordResetCompleteView.as_view(),name="password_reset_complete"),
    path('dashboard',views.dashboard,name='dashboard'),
    path('logout',views.logout,name="logout"),
    path('gold',views.gold,name='gold'),
    path('silver',views.silver,name='silver'),
    path('gold_invoice',views.gold_invoice,name='gold_invoice'),
    path('silver_invoice',views.silver_invoice,name='silver_invoice'), 
    path('rate',views.rate,name='rate'),
    path('generate_gold_invoice/<int:invoice_number>',views.generate_gold_invoice,name="generate_gold_invoice"),
    path('generate_silver_invoice/<int:invoice_number>',views.generate_silver_invoice,name="generate_silver_invoice"),
    path('product',views.product,name="product"),
    path('autocomplete_pid',views.autocomplete_pid,name='autocomplete_pid'),
    path('sold',views.sold,name="sold"),
    path('huid',views.huid,name='huid'),
    path('pid',views.pid,name='pid'),
    path('one_month_statement',views.one_month_statement,name="one_month_statement"),
    path('one_month_silver_statement',views.one_month_silver_statement,name="one_month_silver_statement")
]
