from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse
from base.models import Scholar, Performance, Follow

class ViewProfileTest(APITestCase):
    def setUp(self):
        self.scholar1 = Scholar.objects.create(username="scholar1", email="s1@example.com")
        self.scholar2 = Scholar.objects.create(username="scholar2", email="s2@example.com")
        Follow.objects.create(follower=self.scholar1, followee=self.scholar2)
        
        self.url = reverse('view_profile', kwargs={'pk': self.scholar1.pk})

    def test_view_profile(self):
        response = self.client.get(self.url, )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.data

        self.assertEqual(data['profile_info']['id'], self.scholar1.id)
        self.assertEqual(data['follower_count'], 0)  
        self.assertEqual(data['followee_count'], 1)  

        self.assertEqual(len(data['followers']), 0)
        self.assertEqual(len(data['followees']), 1)
        self.assertEqual(data['followees'][0]['username'], 'scholar2')