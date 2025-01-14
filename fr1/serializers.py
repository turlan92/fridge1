from rest_framework import serializers
from .models import RefrigeratorData

class RefrigeratorDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = RefrigeratorData
        fields = '__all__'
