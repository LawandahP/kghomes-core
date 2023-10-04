from datetime import datetime
from django.http import Http404
from django.utils.translation import gettext_lazy as _


from rest_framework import generics, status
from rest_framework.response import Response

from files.models import Files

from .serializers import BillsSerializer, InvoiceDetailSerializer, InvoiceSerializer, LeaseDetailsSerializer, LeaseSerializer
from leases.models import Bills, Invoice, Lease
from utils.utils import customResponse, logger




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
    
    def get(self, request):
        try:
            leases = self.get_object(request)
            count = len(leases)
            serializer = LeaseDetailsSerializer(leases, many=True)
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
    serializer_class = InvoiceSerializer

    def get_object(self, request):
        queryset = Invoice.objects.filter(account=request.user["account"]["id"])
        # filter = self.filter_queryset(queryset)
        # properties = self.paginate_queryset(filter)
        return queryset


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
            invoices = self.get_object(request)
     
            count = len(invoices)
            serializer = InvoiceDetailSerializer(invoices, many=True)
            return customResponse(
                payload=serializer.data, 
                status=status.HTTP_200_OK, 
                count=count, success=True
            )
        except Exception as e:
            error = {'detail': _(f"An error occurred {e}")}
            return Response(error, status.HTTP_400_BAD_REQUEST)




class InvoiceDetailView(generics.GenericAPIView):
    serializer_class = InvoiceDetailSerializer
    
    def get_object(self, request, id):
        return Invoice.objects.get(id=id, account=request.user["account"]["id"])

    def get(self, request, id):
        try:
            invoice = self.get_object(request, id)
            serializer = self.serializer_class(invoice, many=False)
        except Invoice.DoesNotExist:
            error = {'detail': _("Invoice not found")}
            return Response(error, status.HTTP_404_NOT_FOUND)
        return customResponse(payload=serializer.data, status=status.HTTP_200_OK)

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
