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


class UpdateProfileTest(APITestCase):
    def setUp(self):
        self.scholar = Scholar.objects.create(
            username="testuser",
            email="test@example.com",
            semester=5,
            bio="Test bio",
        )
        self.client.force_authenticate(user=self.scholar)

    def test_update_own_profile_success(self):
        url = reverse('update_profile')
        data = {
            'username': 'updateduser',
            'semester': 6,
            'bio': 'Updated bio',
        }
        response = self.client.put(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.scholar.refresh_from_db()
        self.assertEqual(self.scholar.username, 'updateduser')
        self.assertEqual(self.scholar.semester, 6)
        self.assertEqual(self.scholar.bio, 'Updated bio')

    def test_partial_update(self):
        url = reverse('update_profile')
        data = {'bio': 'Only updating bio'}
        response = self.client.put(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.scholar.refresh_from_db()
        self.assertEqual(self.scholar.bio, 'Only updating bio')
        self.assertEqual(self.scholar.username, 'testuser')  # unchanged

    def test_invalid_data(self):
        url = reverse('update_profile')
        data = {'semester': 15}  # Invalid semester > 8
        response = self.client.put(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)