from collections import defaultdict

from django.shortcuts import render
from rest_framework.views import APIView, Response
from rest_framework.permissions import IsAdminUser
from rest_framework import status
from .models import Service
from django.db import IntegrityError
from django.core.exceptions import ValidationError


class ListServices(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request):
        services = Service.objects.all()
        data = [{'name': s.name, 'url': s.url, 'service_type': s.service_type, 'api_location': s.api_location} for s in
                services]
        return Response({'status': 'success', 'data': data}, status=status.HTTP_200_OK)


class ListServicesByType(APIView):


    def get(self, request):
        # Using defaultdict to automatically handle new service types
        services_by_type = defaultdict(list)

        # Query all services
        services = Service.objects.all()

        # Organize services by their type
        for service in services:
            services_by_type[service.get_service_type_display()].append({
                'name': service.name,
                'url': service.url,
            })

        # Convert defaultdict to regular dict for serialization
        data = dict(services_by_type)
        return Response({'status': 'success', 'data': data}, status=status.HTTP_200_OK)


class AddService(APIView):
    permission_classes = [IsAdminUser]

    def post(self, request):
        data = request.data

        # Validate service_type and api_location
        service_type = data.get('service_type')
        api_location = data.get('api_location')

        valid_service_types = dict(Service.SERVICE_TYPES).keys()
        valid_api_locations = dict(Service.API_LOCATIONS).keys()

        if service_type not in valid_service_types:
            return Response({"status": "error", "message": "Invalid service type."}, status=status.HTTP_400_BAD_REQUEST)

        if api_location not in valid_api_locations:
            return Response({"status": "error", "message": "Invalid API location."}, status=status.HTTP_400_BAD_REQUEST)
        try:
            # Create a new device
            device = Service.objects.create(
                url=data.get('url'),
                name=data.get('name'),
                service_type=data.get('service_type'),
                api_location=data.get('api_location')
            )

            return Response({"status": "success", "message": "Service added successfully."})
        except ValidationError as e:
            return Response({"status": "error", "message": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except IntegrityError as e:
            # Check if the error message is about the 'url' UNIQUE constraint
            if 'UNIQUE constraint failed: service_monitor_service.url' in str(e):
                return Response({"status": "error", "message": "This URL already exists."},
                                status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response({"status": "error", "message": "An error occurred while adding the service."},
                                status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"status": "error", "message": str(e)}, status=status.HTTP_400_BAD_REQUEST)


class DeleteService(APIView):
    permission_classes = [IsAdminUser]

    def delete(self, request, service_name):
        try:
            service = Service.objects.get(name=service_name)
            service.delete()
            return Response({"status": "success", "message": "Service deleted successfully."},
                            status=status.HTTP_204_NO_CONTENT)
        except Service.DoesNotExist:
            return Response({"status": "error", "message": "Service not found."}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"status": "error", "message": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class EditService(APIView):
    permission_classes = [IsAdminUser]

    def patch(self, request, service_name):
        try:
            print(service_name)
            print(request.data)
            service = Service.objects.get(name=service_name)
            data = request.data
            service.name = data.get('name', service.name)
            service.url = data.get('url', service.url)
            service_type = data.get('service_type', service.service_type)
            api_location = data.get('api_location', service.api_location)

            # Validate changes
            if service_type not in dict(Service.SERVICE_TYPES).keys():
                return Response({"status": "error", "message": "Invalid service type."},
                                status=status.HTTP_400_BAD_REQUEST)

            if api_location not in dict(Service.API_LOCATIONS).keys():
                return Response({"status": "error", "message": "Invalid API location."},
                                status=status.HTTP_400_BAD_REQUEST)

            service.service_type = service_type
            service.api_location = api_location
            service.save()

            return Response({"status": "success", "message": "Service updated successfully."})
        except Service.DoesNotExist:
            return Response({"status": "error", "message": "Service not found."}, status=status.HTTP_404_NOT_FOUND)
        except ValidationError as e:
            return Response({"status": "error", "message": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"status": "error", "message": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
