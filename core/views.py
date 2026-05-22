from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework import status
from .models import SystemSettings
from .serializers import SystemSettingsSerializer
from rest_framework.permissions import IsAdminUser

class SystemSettingsViewSet(viewsets.GenericViewSet):
    queryset = SystemSettings.objects.all()
    serializer_class = SystemSettingsSerializer
    permission_classes = [IsAdminUser]

    def list(self, request):
        settings = self.get_queryset()

        serializer = self.get_serializer(settings, many=True)
        return Response(serializer.data)


    def update(self, request, pk=None):
        try:
            settings = SystemSettings.objects.get(key=pk)
        except SystemSettings.DoesNotExist:
            return Response({"detail": "Settings not found"}, status=status.HTTP_404_NOT_FOUND)

        value = request.data.get("value")
        if value is None:
            return Response({"detail": "value is required"}, status=status.HTTP_400_BAD_REQUEST)
        settings.value = value
        settings.save()
        serializer = self.get_serializer(settings)
        return Response(serializer.data)