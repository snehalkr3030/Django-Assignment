from django.urls import path
from . import views



urlpatterns = [
    path('invoices/', views.invoice_list),
    path('invoices/<int:pk>/', views.invoice_detail),
    path('invoices/<int:invoice_pk>/details/', views.invoice_detail_list),
    path('invoices/<int:invoice_pk>/details/<int:detail_id>/', views.invoice_detail_update),
    path('invoices/<int:invoice_pk>/delete/<int:detail_id>/', views.invoice_detail_delete),
]
