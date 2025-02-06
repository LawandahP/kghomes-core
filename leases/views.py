from django.db.models import Sum

import math
from django.utils.translation import gettext_lazy as _
from rest_framework import viewsets

from rest_framework.pagination import PageNumberPagination
from rest_framework import generics, status, viewsets
from rest_framework.response import Response
from bff.utils import UseAuthApi


from files.models import Files
from leases.filters import InvoiceFilter, LeaseFilter

from .serializers import (
    BillsSerializer, InvoiceDetailSerializer, LineItemSerializer,
    InvoiceSerializer, LeaseDetailsSerializer, LeaseSerializer
)
from leases.models import Bills, Invoice, Lease, LineItem
from utils.utils import customResponse, logger


class CustomPaginator(PageNumberPagination):
    page_size = 10
    page_query_param = 'page'
    page_size_query_param = 'size'



class LeaseViewSet(viewsets.ModelViewSet):
    queryset = Lease.objects.all()
    serializer_class = LeaseSerializer
    filterset_class = LeaseFilter
    pagination_class = CustomPaginator

    def get_queryset(self):
        return Lease.objects.filter(account=self.request.user["account"]["id"])

    def create(self, request, *args, **kwargs):
        data = request.data
        user = request.user
        serializer = self.get_serializer(data=data, context={'request': request})
        
        if serializer.is_valid():
            account = user["account"]["id"]
            
            if request.FILES:
                files = request.FILES.getlist("file")
                for i in files:
                    file_instance = Files(file_url=i)
                    file_instance.save()
                    serializer.save(file=file_instance, account=account)

            serializer.save(account=account)
            
            return customResponse(
                message=_("Lease Created Successfully."),
                status=status.HTTP_201_CREATED
            )
        error = {'detail': serializer.errors}
        return Response(error, status.HTTP_400_BAD_REQUEST)

    def list(self, request, *args, **kwargs):
        try:
            leases = self.get_queryset()
            page = self.paginate_queryset(leases)
            if page is not None:
                serializer = LeaseDetailsSerializer(page, many=True)
                return self.get_paginated_response(serializer.data)

            serializer = LeaseDetailsSerializer(leases, many=True)
            tenant_ids = [lease["tenant"] for lease in serializer.data]
            
            try:
                useAuthApi = UseAuthApi("bulk-user-details")
                tenantData = useAuthApi.fetchBulkUserDetails(tenant_ids)
            except:
                logger.warning("Error when fetching user details")
                pass

            for lease in serializer.data:
                tenant_id = lease["tenant"]
                for tenant in tenantData:
                    if tenant["id"] == tenant_id:
                        lease['tenant'] = tenant
                        break

            return customResponse(payload=serializer.data, status=status.HTTP_200_OK, count=len(serializer.data), success=True)
        except Lease.DoesNotExist:
            error = {'detail': _("Lease not found")}
            return Response(error, status.HTTP_404_NOT_FOUND)

        


# Invoices

class CreateInvoiceView(generics.GenericAPIView):
    queryset = Invoice.objects.all()
    serializer_class = InvoiceSerializer
    filterset_class = InvoiceFilter
    search_fields = ['id']
    pagination_class = CustomPaginator
    # authentication_classes = []

    
    def get_all_invoices(self, request):
        invoices = Invoice.objects.filter(account=request.user["account"]["id"])
        return invoices

    def get_object(self, request):
        queryset = Invoice.objects.filter(account=request.user["account"]["id"])
        filter = self.filter_queryset(queryset)
        invoices = self.paginate_queryset(filter)
        return invoices


    def post(self, request):
        serializer = self.serializer_class(
            data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return customResponse(
                payload=serializer.data,
                message=_("Invoice created successfully"),
                status=status.HTTP_201_CREATED
            )
        error = {'detail': serializer.errors}
        return Response(error, status.HTTP_400_BAD_REQUEST)


    def get(self, request):
        try:
            totalCount = len(self.get_all_invoices(request))
            page_size = request.GET.get("size", 10)
            totalpages = math.ceil(totalCount/int(page_size))
            
            invoices = self.get_object(request)  # Assuming this returns a queryset of Django model objects
            logger.info(type(invoices))
            serializer = self.serializer_class(invoices, many=True)
             # Calculate sums

            # Filter by status if needed
            invoices_query = self.get_all_invoices(request)
            status_filter = request.GET.get("status", None)
            if status_filter:
                invoices_query = invoices_query.filter(status=status_filter)
            total_amount_sum = invoices_query.aggregate(Sum('total_amount'))['total_amount__sum'] or 0
            amount_paid_sum = invoices_query.aggregate(Sum('amount_paid'))['amount_paid__sum'] or 0
            balance_sum = invoices_query.aggregate(Sum('balance'))['balance__sum'] or 0

            # Get all tenant IDs
            tenant_ids = [lease["tenant"] for lease in serializer.data]  
            
            modified_invoices = []  # Create a list to store modified invoices
             # Make a single API request to fetch tenant data for all tenants
            try:
                useAuthApi = UseAuthApi("bulk-user-details")
                tenantData = useAuthApi.fetchBulkUserDetails(tenant_ids)
            except:
                logger.warning("Error when fetching user details")
                # raise Exception(_("An error occured while fetching user details"))
                pass
            
            for invoice in serializer.data:
                tenant_id = invoice["tenant"]
                for tenant in tenantData:
                    if tenant["id"] == tenant_id:
                        invoice['tenant'] = tenant
                        modified_invoices.append(invoice)

            count = len(modified_invoices)
            
            filteredPages=math.ceil(count/int(page_size)) 

           
            return customResponse(
                payload=serializer.data, 
                status=status.HTTP_200_OK, 
                count=count, 
                totalCount=totalCount,
                totalPages=totalpages,
                totalFilteredPages=filteredPages,

                totalAmount=total_amount_sum,  
                totalAmountPaid=amount_paid_sum,
                totalBalance=balance_sum,

                success=True
            )
        except Exception as e:
            error = {'detail': _(f"{e}")}
            return Response(error, status.HTTP_400_BAD_REQUEST)
        
class InvoiceDetailView(generics.GenericAPIView):
    serializer_class = InvoiceDetailSerializer
    authentication_classes = []
    
    def get_object(self, request, id):
        return Invoice.objects.get(id=id)

    def get(self, request, id):
        try:
            invoice = self.get_object(request, id)
            serializer = self.serializer_class(invoice, many=False)
            
            invoice_data = serializer.data
            tenant_id = invoice_data["tenant"]  # Get the tenant ID from the serialized data
            
            # fetch tenant details
            try:
                useAuthApi = UseAuthApi("user-details")
                tenantData = useAuthApi.fetchUserDetails(tenant_id)
                invoice_data['tenant'] = tenantData
                return customResponse(payload=invoice_data, status=status.HTTP_200_OK)
            except:
                return customResponse(payload=serializer.data, status=status.HTTP_200_OK)
                
           
        except Exception as e:
            error = {'detail': _(f"{e}")}
            return Response(error, status.HTTP_404_NOT_FOUND)
       
    

    def patch(self, request, id):
        invoice = self.get_object(request, id=id)
        serializer = InvoiceSerializer(
            invoice, data=request.data, partial=True)

        if serializer.is_valid():
            serializer.save()
            # audit(request=request,
            #       action_flag=f"Updated Invoice for {invoice.invoice_id}")
            return customResponse(
                payload=serializer.data,
                message=_("Invoice updated successfully"),
                status=status.HTTP_200_OK
            )
        error = {'detail': serializer.errors}
        return Response(error, status.HTTP_404_NOT_FOUND)


    def delete(self, request, id):
        try:
            invoice = self.get_object(request=request, id=id)
            invoice.delete()
            return customResponse(
                message=_("Invoice deleted successfully"), 
                status=status.HTTP_200_OK
            )
        except Invoice.DoesNotExist:
            error = {'detail': _("Invoice Not Found")}
            return Response(error, status.HTTP_404_NOT_FOUND)




# ################################## Bills Section ##############################################

class BillsCreateListView(generics.GenericAPIView):
    serializer_class = BillsSerializer

    # filterset_class = InvoiceFilter

    def get_object(self, request):
        return self.filter_queryset(Bills.objects.all())

    
    def post(self, request):
        serializer = self.serializer_class(data=request.data, context={'request': request})
        
        if serializer.is_valid():
            serializer.save()
            return customResponse(
                message=_("Bill added successfully"),
                status=status.HTTP_201_CREATED
            )
        error = {'detail': serializer.errors}
        return Response(error, status.HTTP_400_BAD_REQUEST)

    
    def get(self, request):
        try:
            bill = self.get_object(request)
        except Exception as e:
            error = {'detail': [e]}
            return Response(error, status.HTTP_400_BAD_REQUEST)
        count = bill.count()
        serializer = self.serializer_class(
            bill, many=True, context={'request': request})
        return customResponse(payload=serializer.data, status=status.HTTP_200_OK, count=count)


class BillDetailView(generics.GenericAPIView):
    serializer_class = BillsSerializer

    def get_object(self, request, id):
        return Bills.objects.get(id=id)

    def get(self, request, id):
        try:
            bill = self.get_object(request, id=id)
            serializer = self.serializer_class(bill, many=False)
            return customResponse(payload=serializer.data, status=status.HTTP_200_OK)
        except Bills.DoesNotExist:
            error = {'detail': _("Bill Not Found")}
            return Response(error, status.HTTP_404_NOT_FOUND)

    
    def patch(self, request, id):
        bill = self.get_object(request, id=id)
        serializer = self.serializer_class(
            bill, data=request.data, partial=True)

        if serializer.is_valid():
            serializer.save()
            # audit(request=request, action_flag=f"Updated Bill for {bill.id}")
            return customResponse(
                message=_("Bill updated successfully"),
                status=status.HTTP_200_OK
            )
        error = {'detail': serializer.errors}
        return Response(error, status.HTTP_404_NOT_FOUND)
    


    
    def delete(self, request, id):
        try:
            invoice = self.get_object(request=request, id=id)
            invoice.delete()
            return customResponse(message=_("Bill deleted successfully"), status=status.HTTP_200_OK)
        except Bills.DoesNotExist:
            error = {'detail': _("Bill Not Found")}
            return Response(error, status.HTTP_404_NOT_FOUND)
 
# request.user["account"]["id"]
# Line Item
class LineItemViewSet(viewsets.ModelViewSet):
    serializer_class = LineItemSerializer
    queryset = LineItem.objects.all()
    pagination_class = None  # Disable pagination
    filter_backends = []  # Disable filtering



    def get_queryset(self):
        user_account_id = self.request.user["account"]["id"]
        return LineItem.objects.filter(account=user_account_id)
    
    
