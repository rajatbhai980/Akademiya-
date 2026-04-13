from rest_framework import serializers
from base.models import Scholar


class ScholarPerformanceSerializer(serializers.ModelSerializer):
    level = serializers.IntegerField(source='performance.level')

    class Meta:
        model = Scholar
        fields = ['username', 'level']
