from django.test import TestCase
from django.urls import reverse

class DashboardViewTest(TestCase):
    def test_dashboard_renders(self):
        response = self.client.get(reverse('dashboard'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'normapy/dashboard.html')
