from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from django.contrib import admin
from .utils import get_data

MAX_MORTGAGE_TERM_YEARS = 40


class Search(models.Model):
    DOWN_PAYMENT_CHOICES = [
        ("percentage", "Percentage (%)"),
        ("amount", "Amount ($)"),
    ]

    TERM_UNIT_CHOICES = [
        ("months", "Months"),
        ("years", "Years"),
    ]

    purchase_price = models.DecimalField(
        verbose_name="purchase price",
        max_digits=15,
        decimal_places=2,
        validators=[MinValueValidator(1.0)],
    )
    down_payment_in = models.CharField(
        verbose_name="Enter down payment as amount or percentage",
        max_length=20,
        choices=DOWN_PAYMENT_CHOICES,
        default="amount",
    )
    down_payment = models.DecimalField(
        verbose_name="down payment",
        max_digits=15,
        decimal_places=2,
        validators=[MinValueValidator(0.0)],
    )
    mortgage_term_unit = models.CharField(
        verbose_name="Enter mortgage term in months or years",
        max_length=10,
        choices=TERM_UNIT_CHOICES,
        default="years",
    )
    mortgage_term = models.IntegerField(
        verbose_name="mortgage term", validators=[MinValueValidator(1)]
    )
    interest_rate = models.DecimalField(
        max_digits=6,
        decimal_places=3,
        validators=[
            MinValueValidator(0.0),
            MaxValueValidator(100.0),
        ],
    )
    total_loan_amt = models.DecimalField(
        verbose_name="Total loan amount",
        max_digits=15,
        decimal_places=2,
        validators=[MinValueValidator(0.0)],
        blank=True,
        null=True,
    )
    monthly_payment = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        validators=[MinValueValidator(0.0)],
        blank=True,
        null=True,
    )
    total_amt_paid = models.DecimalField(
        verbose_name="Total amount paid over the course of the loan",
        max_digits=15,
        decimal_places=2,
        validators=[MinValueValidator(0.0)],
        blank=True,
        null=True,
    )
    total_interest_paid = models.DecimalField(
        verbose_name="Total interest paid over the course of the loan",
        max_digits=15,
        decimal_places=2,
        validators=[MinValueValidator(0.0)],
        blank=True,
        null=True,
    )

    class Meta:
        indexes = [
            models.Index(
                fields=[
                    "purchase_price",
                    "down_payment_in",
                    "down_payment",
                    "mortgage_term_unit",
                    "mortgage_term",
                    "interest_rate",
                ]
            )
        ]
        constraints = [
            models.UniqueConstraint(
                fields=[
                    "purchase_price",
                    "down_payment_in",
                    "down_payment",
                    "mortgage_term_unit",
                    "mortgage_term",
                    "interest_rate",
                ],
                name="unique_mortgage_entry",
            )
        ]

    def get_amount(self):
        return (
            self.purchase_price * self.down_payment / 100
            if self.down_payment_in == "percentage"
            else self.down_payment
        )

    def clean(self):

        if self.down_payment_in == "percentage" and self.down_payment >= 100.0:
            raise ValidationError(
                "Down payment can't be greater than / equal to purchase price"
            )

        if self.purchase_price <= self.get_amount():
            raise ValidationError(
                "Purchase price can't be lesser than / equal to down payment"
            )

        if (
            self.mortgage_term_unit == "months"
            and self.mortgage_term > MAX_MORTGAGE_TERM_YEARS * 12
        ):
            raise ValidationError("Mortgage term months can't be greater than 480")

        if (
            self.mortgage_term_unit == "years"
            and self.mortgage_term > MAX_MORTGAGE_TERM_YEARS
        ):
            raise ValidationError("Mortgage term years can't be greater than 40")

    def __str__(self):
        ret = [f"purchase - {self.purchase_price}, ", "down-payment - "]
        if self.down_payment_in == "amount":
            ret.append(f"${self.down_payment}, ")
        else:
            ret.append(f"{self.down_payment}%, ")
        ret.append(f"mortgage term - {self.mortgage_term} {self.mortgage_term_unit}")

        return "".join(ret)

    def save(
        self,
        *args,
        force_insert=False,
        force_update=False,
        using=None,
        update_fields=None,
        **kwargs,
    ):
        try:
            self.full_clean()
            loan = self.purchase_price - self.get_amount()
            if self.mortgage_term_unit == "months":
                mortgage_term = self.mortgage_term / 12
            else:
                mortgage_term = self.mortgage_term
            monthly_payment, total_interest_paid = get_data(
                loan, self.interest_rate, mortgage_term
            )
            self.total_loan_amt = loan
            self.monthly_payment = monthly_payment
            self.total_amt_paid = loan + total_interest_paid
            self.total_interest_paid = total_interest_paid

            super().save(*args, **kwargs)
        except Exception as e:
            print(f"Issue handling request: {e}")


class SearchAdmin(admin.ModelAdmin):
    readonly_fields = [
        "total_loan_amt",
        "monthly_payment",
        "total_amt_paid",
        "total_interest_paid",
    ]
