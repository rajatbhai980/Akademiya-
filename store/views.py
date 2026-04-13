from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from .serializers import *
from base.models import Scholar


@api_view(['post'])
@permission_classes([IsAuthenticated])
def purchase_subscription(request):
    scholar = request.user

    if scholar.gems < 700:
        return Response(
            {"detail": "Not enough gems to purchase subscription."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    if scholar.subscribed:
        return Response(
            {
                "detail": "Scholar is already subscribed.",
                "subscribed": True,
                "gems": scholar.gems,
            },
            status=status.HTTP_200_OK,
        )

    scholar.gems -= 700
    scholar.subscribed = True
    scholar.save(update_fields=['gems', 'subscribed'])

    return Response(
        {
            "subscribed": scholar.subscribed,
            "gems": scholar.gems,
        },
        status=status.HTTP_200_OK,
    )
