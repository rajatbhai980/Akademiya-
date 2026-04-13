from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse
from base.models import Scholar


class SubscriptionPurchaseTest(APITestCase):
    def setUp(self):
        self.url = reverse('purchase_subscription')

    def test_purchase_subscription_requires_authentication(self):
        response = self.client.post(self.url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_purchase_subscription_fails_when_not_enough_gems(self):
        scholar = Scholar.objects.create(email='test@example.com', gems=500)
        self.client.force_authenticate(user=scholar)

        response = self.client.post(self.url)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['detail'], 'Not enough gems to purchase subscription.')
        scholar.refresh_from_db()
        self.assertFalse(scholar.subscribed)
        self.assertEqual(scholar.gems, 500)

    def test_purchase_subscription_succeeds_and_marks_subscribed(self):
        scholar = Scholar.objects.create(email='rich@example.com', gems=700)
        self.client.force_authenticate(user=scholar)

        response = self.client.post(self.url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['subscribed'], True)
        self.assertEqual(response.data['gems'], 0)

        scholar.refresh_from_db()
        self.assertTrue(scholar.subscribed)
        self.assertEqual(scholar.gems, 0)

    def test_purchase_subscription_returns_ok_when_already_subscribed(self):
        scholar = Scholar.objects.create(email='subscribed@example.com', gems=1200, subscribed=True)
        self.client.force_authenticate(user=scholar)

        response = self.client.post(self.url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['detail'], 'Scholar is already subscribed.')
        self.assertEqual(response.data['subscribed'], True)
        self.assertEqual(response.data['gems'], 1200)
