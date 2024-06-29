from django.http import JsonResponse
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import NetworkDevice
from .utilities import update_prometheus_targets, remove_prometheus_targets
import json
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAdminUser


class AddDevice(APIView):
    permission_classes = [IsAdminUser]
    def post(self, request):
        data = request.data
        try:
            update_prometheus_targets([data.get('ip_address')])
            # Create a new device
            device = NetworkDevice.objects.create(
                name=data.get('name'),
                device_type=data.get('device_type'),
                ip_address=data.get('ip_address')
            )

            return Response({"status": "success", "message": "Device added successfully."})

        except Exception as e:
            return Response({"status": "error", "message": str(e)}, status=status.HTTP_400_BAD_REQUEST)


class UpdateDevices(APIView):
    permission_classes = [IsAdminUser]
    def post(self, request):
        try:
            data = json.loads(request.body)
            old_ip_address = data.get('old_ip_address')
            new_device_data = data.get('new_device_data')

            # Find the device by old IP address
            device = NetworkDevice.objects.get(ip_address=old_ip_address)
            # Prepare updates but don't save yet
            new_ip_address = new_device_data.get('ip_address', device.ip_address)
            if old_ip_address != new_ip_address:
                # Update Prometheus targets first, if the IP address has changed
                remove_prometheus_targets([old_ip_address])
                update_prometheus_targets([new_ip_address])

            # Update the device details
            device.name = new_device_data.get('name', device.name)
            device.device_type = new_device_data.get('device_type', device.device_type)
            device.ip_address = new_device_data.get('ip_address', device.ip_address)

            # Save the updated device
            device.save()

            return Response({"status": "success", "message": "Device updated successfully."})
        except NetworkDevice.DoesNotExist:
            return Response({"status": "error", "message": "Device not found."}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"status": "error", "message": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class DeleteDevice(APIView):
    permission_classes = [IsAdminUser]
    def post(self, request):
        try:
            ip_address = request.data.get('ip_address')

            # Ensure IP address exists
            device = NetworkDevice.objects.get(ip_address=ip_address)

            # Attempt to remove from Prometheus targets first
            remove_prometheus_targets([ip_address])

            # If successful, delete the device from the database
            device.delete()

            return Response({"status": "success", "message": "Device deleted successfully."})
        except NetworkDevice.DoesNotExist:
            return Response({"status": "error", "message": "Device not found."}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"status": "error", "message": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class ListDevices(APIView):
    permission_classes = [IsAdminUser]
    def get(self, request):
        devices = NetworkDevice.objects.all()
        data = [{"name": device.name, "device_type": device.device_type, "ip_address": device.ip_address} for device in
                devices]
        return JsonResponse(data, safe=False)