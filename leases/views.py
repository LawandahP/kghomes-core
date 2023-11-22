from datetime import datetime
import json
import math
from django.conf import settings
from django.http import Http404
from django.utils.translation import gettext_lazy as _
from rest_framework import serializers
import requests  # Import HttpResponse for Django response

from rest_framework.pagination import PageNumberPagination
from rest_framework import generics, status
from rest_framework.response import Response
from bff.utils import UseAuthApi


from files.models import Files
from leases.filters import InvoiceFilter

from .serializers import BillsSerializer, InvoiceDetailSerializer, InvoiceSerializer, LeaseDetailsSerializer, LeaseSerializer
from leases.models import Bills, Invoice, Lease
from utils.utils import customResponse, logger


class CustomPaginator(PageNumberPagination):
    page_size = 10
    page_query_param = 'page'
    page_size_query_param = 'size'


class CreatViewLease(generics.GenericAPIView):
    serializer_class = LeaseSerializer
    

    def get_object(self, request):
        queryset = Lease.objects.filter(account=request.user["account"]["id"])
        # filter = self.filter_queryset(queryset)
        # properties = self.paginate_queryset(filter)
        return queryset


    def post(self, request):
        data = request.data
        user = request.user
        
        serializer = self.serializer_class(data=data, context={'request': request})
        if serializer.is_valid():
            account = user["account"]["id"]
            
            if request.FILES:
                files = request.FILES.getlist("file")
                # logger.critical(files)
                
                for i in files:
                    file_instance = Files(file_url=i)
                    file_instance.save()
                    serializer.save(file=file_instance, account=account)

            serializer.save(account=account)            
            
            return customResponse(
                payload=serializer.data,
                message=_("Lease Created Successfully."),
                status=status.HTTP_201_CREATED
            )
        error = {'detail': serializer.errors}
        return Response(error, status.HTTP_400_BAD_REQUEST)
    
    # def get(self, request):
    #     try:
    #         leases = self.get_object(request)
    #         count = len(leases)
    #         serializer = LeaseDetailsSerializer(leases, many=True)
    #         return customResponse(payload=serializer.data, status=status.HTTP_200_OK, count=count, success=True)
    #     except Lease.DoesNotExist:
    #         error = {'detail': _("Lease not found")}
    #         return Response(error, status.HTTP_404_NOT_FOUND)
    def get(self, request):
        try:
            leases = self.get_object(request)
            count = len(leases)
            serializer = LeaseDetailsSerializer(leases, many=True)

            modified_invoices = []  # Create a list to store modified leases
            
            for lease in serializer.data:
                tenant_id = lease["tenant"]  # Get the tenant ID from the serialized data

                # Make an API request to fetch tenant data based on tenant_id
                try:
                    useAuthApi = UseAuthApi("user-details")
                    tenantData = useAuthApi.fetchUserDetails(tenant_id)
                    lease['tenant'] = tenantData
                    modified_invoices.append(lease)
                except:
                    modified_invoices.append(lease)

            return customResponse(payload=serializer.data, status=status.HTTP_200_OK, count=count, success=True)
        except Lease.DoesNotExist:
            error = {'detail': _("Lease not found")}
            return Response(error, status.HTTP_404_NOT_FOUND)



class LeaseDetailView(generics.GenericAPIView):
    serializer_class = LeaseSerializer

    def get_object(self, request, id):
        return Lease.objects.get(id=id)

    # 
    def get(self, request, id):
        try:
            lease = self.get_object(request, id)
            serializer = self.serializer_class(lease, many=False)
        except Lease.DoesNotExist:
            error = {'detail': "Lease not found"}
            return Response(error, status.HTTP_404_NOT_FOUND)
        return customResponse(payload=serializer.data, status=status.HTTP_200_OK)

    # @method_decorator(group_required('REALTOR'))
    def patch(self, request, id):
        try:
            lease = self.get_object(request=request, id=id)
            serializer = self.serializer_class(lease, data=request.data, partial=True)

            if serializer.is_valid():
                serializer.save()
                #     audit(request=request, action_flag=f"Updated {request.data} for Lease {lease.name}")
                return customResponse(
                    payload=serializer.data,
                    message=_("Lease updated successfully"),
                    status=status.HTTP_200_OK
                )
            error = {'detail': serializer.errors}
            return Response(error, status.HTTP_400_BAD_REQUEST)
        except Lease.DoesNotExist:
            error = {'detail': _("Lease not found")}
            return Response(error, status.HTTP_404_NOT_FOUND)

   
    # @method_decorator(group_required('REALTOR'))
    def delete(self, request, id):
        try:
            lease = self.get_object(request=request, id=id)
            lease.delete()
            return customResponse(message=_("Lease deleted successfully"), status=status.HTTP_200_OK)
        except Lease.DoesNotExist:
            error = {'detail': _("Lease Not Found")}
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
        return len(invoices)

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
            totalCount = self.get_all_invoices(request)
            page_size = request.GET.get("size", 10)
            totalpages=math.ceil(totalCount/int(page_size))
            
            invoices = self.get_object(request)  # Assuming this returns a queryset of Django model objects
            serializer = self.serializer_class(invoices, many=True)
            
            modified_invoices = []  # Create a list to store modified invoices

            for invoice in serializer.data:
                tenant_id = invoice["tenant"]  # Get the tenant ID from the serialized data

                # Make an API request to fetch tenant data based on tenant_id
                try:
                    useAuthApi = UseAuthApi("user-details")
                    tenantData = useAuthApi.fetchUserDetails(tenant_id)
                    invoice['tenant'] = tenantData
                    modified_invoices.append(invoice)
                except:
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
        serializer = self.serializer_class(
            data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return customResponse(
                payload=serializer.data,
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
                payload=serializer.data,
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
