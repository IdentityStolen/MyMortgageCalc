from django.core.exceptions import ValidationError
from django.test import TestCase

from .models import Search
from .utils import get_data


class SearchTest(TestCase):
    def test_get_data(self):
        expected = (898, 123312)

        actual = get_data(200000, 3.5, 30)
        print(actual)
        self.assertEqual(actual, expected)

    def test_down_payment_percent(self):
        search = Search.objects.create(
            purchase_price=20,
            down_payment_in="percentage",
            down_payment=100,
            mortgage_term_unit="months",
            mortgage_term=360,
            interest_rate=3.5,
        )
        self.assertRaises(ValidationError)

    def test_down_payment_amount(self):
        search = Search.objects.create(
            purchase_price=20,
            down_payment_in="amount",
            down_payment=100,
            mortgage_term_unit="months",
            mortgage_term=360,
            interest_rate=3.5,
        )
        self.assertRaises(ValidationError)

    def test_mortgage_term_months(self):
        search = Search.objects.create(
            purchase_price=20,
            down_payment_in="amount",
            down_payment=10,
            mortgage_term_unit="months",
            mortgage_term=481,
            interest_rate=3.5,
        )
        self.assertRaises(ValidationError)

    def test_mortgage_term_years(self):
        search = Search.objects.create(
            purchase_price=20,
            down_payment_in="amount",
            down_payment=10,
            mortgage_term_unit="years",
            mortgage_term=41,
            interest_rate=3.5,
        )
        self.assertRaises(ValidationError)

    def test_mortgage_term_years_ok(self):
        search = Search.objects.create(
            purchase_price=20,
            down_payment_in="amount",
            down_payment=10,
            mortgage_term_unit="years",
            mortgage_term=40,
            interest_rate=3.5,
        )
        self.assertRaises(ValidationError)

    def test_mortgage_calculator_ok(self):
        search = Search.objects.create(
            purchase_price=400000,
            down_payment_in="amount",
            down_payment=200000,
            mortgage_term_unit="years",
            mortgage_term=30,
            interest_rate=3.5,
        )
        self.assertEqual(search.total_loan_amt, 200000)
        self.assertEqual(search.monthly_payment, 898)
        self.assertEqual(search.total_interest_paid, 123312)
        self.assertEqual(search.total_amt_paid, 323312)

    def test_mortgage_calculator_percentage_ok(self):
        search = Search.objects.create(
            purchase_price=400000,
            down_payment_in="percentage",
            down_payment=20.00,
            mortgage_term_unit="years",
            mortgage_term=30,
            interest_rate=3.5,
        )
        self.assertEqual(search.total_loan_amt, 320000)
        self.assertEqual(search.monthly_payment, 1437)
        self.assertEqual(search.total_interest_paid, 197299)
        self.assertEqual(search.total_amt_paid, 517299)
