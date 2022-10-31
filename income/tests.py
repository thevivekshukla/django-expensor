import datetime

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from income.forms import IncomeForm
from income.models import Income, Source
from utils.helpers import default_date_format, get_ist_datetime


# Create your tests here.

class IncomeViewTestCase(TestCase):
    """
    Test cases for income views.
    """

    def setUp(self) -> None:
        """
        Creating data to test views.
        """
        self.user = get_user_model().objects.create_user(
            username='test_user',
            email='test_user@gmail.com',
            password='asdfghjkl'
        )
        self.client.force_login(self.user)

        source = Source.objects.create(
            user=self.user,
            name='test_source'
        )
        Income.objects.create(
            user=self.user,
            amount=2000,
            source=source,
            timestamp=datetime.datetime.now()
        )

    def test_user_is_authenticated(self):
        """
        The income list page contain
        username on the right corner
        if the user is authenticated.
        """
        response = self.client.get(reverse('income:add-income'))
        self.assertContains(response, self.user.username)
        self.assertTrue(self.user.is_authenticated)

    def test_income_add_view_template(self):
        """
        The income add view uses `add_income.html`.
        """
        response = self.client.get(reverse('income:add-income'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'add_income.html')

    def test_income_list_view_template(self):
        """
        The all income list view uses
        `income_list.html`.
        """
        response = self.client.get(reverse('income:income-list'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'income_list.html')

    def test_yearly_income_list_view_template(self):
        """
        The yearly income list view uses
        `year-income.html`.
        """
        response = self.client.get(reverse('income:year-income-list'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'year-income.html')

    def test_monthly_list_view_template(self):
        """
        The monthly income list view uses
        `month-income.html`
        """
        response = self.client.get(reverse('income:month-income-list'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'month-income.html')

    def test_income_add_form_is_valid(self):
        """
        The income add form is valid if
        the data is proper.
        """
        form = IncomeForm(
            data={
                'user': self.user,
                'timestamp': datetime.datetime.now(),
                'amount': 1200,
                'source': 'test_source'
            }
        )
        self.assertEqual(
            form.fields['timestamp'].initial,
            default_date_format(get_ist_datetime())
        )
        self.assertTrue(form.is_valid())

    def test_income_add_form_is_not_valid(self):
        """
        The income add form is not valid if
        the data is not proper.
        """
        form = IncomeForm(
            data={
                'user': self.user,
                'timestamp': '08/10/22',
                'amount': '2000',
                'source': 'test_source'
            }
        )
        self.assertFalse(form.is_valid())

    def test_user_income_list(self):
        """
        The income list contains all income
        created by user.
        """
        user_income = Income.objects.filter(user=self.user).order_by(
            '-timestamp', '-created_at'
        )
        response = self.client.get(reverse('income:income-list'))
        self.assertQuerysetEqual(
            response.context['objects'],
            user_income,
            transform=lambda x: x
        )
