from datetime import datetime
from django.utils import timezone
import pytz
from rest_framework.response import Response
from rest_framework import status, generics
from config.permissions import IsRealtor
from payments.filters import PaymentFilter

from utils.utils import CustomPagination, customResponse
from .models import Payment
from .serializers import PaymentDetailsSerializer, PaymentSerializer

class PaymentListCreate(generics.GenericAPIView):
    queryset = Payment.objects.all()  # Set your queryset here
    pagination_class = CustomPagination
    serializer_class = PaymentSerializer
    # permission_classes = [IsRealtor]

    filterset_class = PaymentFilter
    search_fields = ['PhoneNumber']


    def get_object(self, request):
        queryset = Payment.objects.filter(account=request.user["account"]["id"])
        filter = self.filter_queryset(queryset)
        payments = self.paginate_queryset(filter)
        return payments
    
    def get(self, request):
        payments = self.get_object(request)
        serializer = PaymentDetailsSerializer(payments, many=True)
        # return Response(serializer.data)
        return customResponse(payload=serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        pay_for = request.GET.get('payFor', None)
        user = request.user

        print("time", request.data["TransactionDate"])
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