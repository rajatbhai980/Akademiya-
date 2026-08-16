from rest_framework import serializers
from base.models import Scholar


class ScholarPerformanceSerializer(serializers.ModelSerializer):
    level = serializers.IntegerField(source='performance.level')
    photo = serializers.ImageField(use_url=True, allow_null=True, required=False)

    class Meta:
        model = Scholar
        fields = ['id', 'photo', 'username', 'level']
