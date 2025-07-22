"""API views and endpoints."""
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from .models import Company
from .serializers import CompanySerializer


@api_view(["GET", "POST"])
def company_profile(request):
    if request.method == "GET":
        try:
            company = Company.objects.get(user=request.user)
            return Response(CompanySerializer(company).data)
        except Company.DoesNotExist:
            return Response({"error": "Company profile not found"}, status=status.HTTP_404_NOT_FOUND)

    elif request.method == "POST":
        try:
            company = Company.objects.get(user=request.user)
            serializer = CompanySerializer(company, data=request.data, partial=True)
        except Company.DoesNotExist:
            serializer = CompanySerializer(data=request.data)

        if serializer.is_valid():
            serializer.save(user=request.user)
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
