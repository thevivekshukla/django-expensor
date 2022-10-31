import datetime

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from expense.models import Expense, Remark


class AddExpenseViewTestCase(TestCase):
    """
    Test case for add expense view.
    """

    def setUp(self):
        """
        Creating data to test views.
        """
        self.user = get_user_model().objects.create_user(
            username='test_user',
            email='test_user@gmail.com',
            password='asdfghjkl'
        )
        self.client.force_login(self.user)

    def test_index_view_status_code(self):
        """
        The index page returns status_code 200.
        """
        response = self.client.get(reverse('expense:add_expense'))
        self.assertEqual(response.status_code, 200)

    def test_user_is_authenticated(self):
        """
        The index page contain username on
        the right corner if the user
        is authenticated.
        """
        response = self.client.get(reverse('expense:add_expense'))
        self.assertContains(response, self.user.username)

    def test_user_expense_list(self):
        """
        The expense list view contains
        all expense created by user.
        """
        remark = 'test_remark'
        remark_obj = Remark.objects.create(
            user=self.user,
            name=remark
        )
        timestamp = datetime.datetime.now()
        Expense.objects.create(
            user=self.user,
            amount=2000,
            timestamp=timestamp,
            remark=remark_obj
        )
        user_expenses = Expense.objects.all(user=self.user)
        response = self.client.get(reverse('expense:expense_list'))
        self.assertQuerysetEqual(
            response.context['objects'],
            user_expenses,
            transform=lambda x: x
        )

    def test_no_expense(self):
        """
        The expense list page contains "Nothing found"
        when expense is empty.
        """
        response = self.client.get(reverse('expense:expense_list'))
        self.assertContains(response, 'Nothing found')
        self.assertQuerysetEqual(
            response.context['objects'],
            [], transform=lambda x: x
        )
