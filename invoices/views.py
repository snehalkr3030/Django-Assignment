from django.shortcuts import render
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .models import Invoice, InvoiceDetail
from .serializers import InvoiceSerializer, InvoiceDetailSerializer

@api_view(['GET', 'POST'])
def invoice_list(request):
    if request.method == 'GET':
        invoices = Invoice.objects.all()
        serializer = InvoiceSerializer(invoices, many=True)
        return Response(serializer.data)

    elif request.method == 'POST':
        serializer = InvoiceSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            # Create associated invoice details
            invoice_details_data = request.data.get('invoice_details', [])
            for detail_data in invoice_details_data:
                detail_data['invoice'] = serializer.data['id']
                detail_serializer = InvoiceDetailSerializer(data=detail_data)
                if detail_serializer.is_valid():
                    detail_serializer.save()
                else:
                    # Rollback if detail serializer is not valid
                    Invoice.objects.get(id=serializer.data['id']).delete()
                    return Response(detail_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET', 'PUT', 'DELETE'])
def invoice_detail(request, pk):
    try:
        invoice = Invoice.objects.get(pk=pk)
    except Invoice.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        serializer = InvoiceSerializer(invoice)
        return Response(serializer.data)

    elif request.method == 'PUT':
        serializer = InvoiceSerializer(invoice, data=request.data)
        if serializer.is_valid():
            serializer.save()
            # Update associated invoice details
            invoice_details_data = request.data.get('invoice_details', [])
            for detail_data in invoice_details_data:
                detail_data['invoice'] = serializer.data['id']
                detail_pk = detail_data.pop('id', None)
                if detail_pk:
                    try:
                        detail = InvoiceDetail.objects.get(pk=detail_pk, invoice=serializer.data['id'])
                    except InvoiceDetail.DoesNotExist:
                        continue
                    detail_serializer = InvoiceDetailSerializer(detail, data=detail_data)
                else:
                    detail_serializer = InvoiceDetailSerializer(data=detail_data)
                if detail_serializer.is_valid():
                    detail_serializer.save()
                else:
                    return Response(detail_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'DELETE':
        invoice.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

@api_view(['GET', 'POST'])
def invoice_detail_list(request, invoice_pk):
    try:
        invoice = Invoice.objects.get(pk=invoice_pk)
    except Invoice.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        details = invoice.details.all()
        serializer = InvoiceDetailSerializer(details, many=True)
        return Response(serializer.data)

    elif request.method == 'POST':
        request.data['invoice'] = invoice.pk
        serializer = InvoiceDetailSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['PUT',])
def invoice_detail_update(request, invoice_pk, detail_id):
    try:
        invoice_detail = InvoiceDetail.objects.get(invoice=invoice_pk, id=detail_id)
    except InvoiceDetail.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    if request.method == 'PUT':
        serializer = InvoiceDetailSerializer(invoice_detail, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

@api_view(['DELETE'])
def invoice_detail_delete(request, invoice_pk, detail_id):
    try:
        invoice_detail = InvoiceDetail.objects.get(invoice=invoice_pk, id=detail_id)
    except InvoiceDetail.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    if request.method == 'DELETE':
        invoice_detail.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)