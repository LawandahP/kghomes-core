from django.db.models import Sum
from django.utils.translation import gettext_lazy as _

import math
from rest_framework.response import Response
from rest_framework import status, generics
from bff.utils import UseAuthApi
from config.permissions import IsRealtor
from payments.filters import PaymentFilter

from utils.utils import CustomPagination, customResponse, logger
from .models import Payment
from .serializers import PaymentDetailsSerializer, PaymentSerializer

class PaymentListCreate(generics.GenericAPIView):
    queryset = Payment.objects.all()  # Set your queryset here
    pagination_class = CustomPagination
    serializer_class = PaymentSerializer
    # permission_classes = [IsRealtor]

    filterset_class = PaymentFilter
    search_fields = ['PhoneNumber']

    def get_all_payments(self, request):
        payment = Payment.objects.filter(account=request.user["account"]["id"])
        return payment
    
    def get_object(self, request):
        queryset = Payment.objects.filter(account=request.user["account"]["id"])
        filter = self.filter_queryset(queryset)
        payments = self.paginate_queryset(filter)
        return payments
    
    def get(self, request):

        try:
            totalCount = len(self.get_all_payments(request))
            page_size = request.GET.get("size", 10)
            totalpages = math.ceil(totalCount/int(page_size))

            payments = self.get_object(request)  # Assuming this returns a queryset of Django model objects
            serializer = PaymentDetailsSerializer(payments, many=True)

            # get sum
            payments_query = self.get_all_payments(request)
            total_amount_sum = payments_query.aggregate(Sum('Amount'))['Amount__sum'] or 0

            filteredPages=math.ceil(totalCount/int(page_size)) 

            # Get all tenant IDs
            tenant_ids = [payment.get("PaidFor", "") for payment in serializer.data]   
    
            # Make a single API request to fetch tenant data for all tenants
            try:
                useAuthApi = UseAuthApi("bulk-user-details")
                tenantData = useAuthApi.fetchBulkUserDetails(tenant_ids)
                logger.info(tenantData)
            except:
                logger.warning("Error when fetching user details")
                # raise Exception(_("An error occured while fetching user details"))
                tenantData = []
                pass

            # Replace tenant IDs with corresponding tenant data
            for payment in serializer.data:
                tenant_id = payment["PaidFor"]
                found = False  # Flag to check if tenant_id is found
                for tenant in tenantData:
                    # Check if tenant is not empty and has the key 'id'
                    if tenant and "id" in tenant and tenant["id"] == tenant_id:
                        payment['PaidFor'] = tenant
                        found = True
                        break
                if not found:
                    # Set to empty dict if tenant_id is not found
                    payment["PaidFor"] = None

            return customResponse(
                payload=serializer.data, 
                status=status.HTTP_200_OK, 
                count=totalCount, 
                totalCount=totalCount,
                totalPages=totalpages,
                totalFilteredPages=filteredPages,

                totalAmount=total_amount_sum,  

                success=True
            )
        except Exception as e:
            error = {'detail': _(f"{e}")}
            return Response(error, status.HTTP_400_BAD_REQUEST)


    def post(self, request):
        pay_for = request.GET.get('payFor', None)
        user = request.user

        if pay_for:
            request.data['PayFor'] = pay_for
        # get user account
        account = user["account"]["id"]
        
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            serializer.save(account=account)
            return customResponse(
                payload=serializer.data,
                message=f"Payment Successfull",
                status=status.HTTP_201_CREATED
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)