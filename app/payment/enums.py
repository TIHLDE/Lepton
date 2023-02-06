from enum import Enum
from django.db.models import TextChoices

class OrderStatus(TextChoices):
    INITIATE = "INITIATE",
    RESERVE = "RESERVE",
    CAPTURE = "CAPTURE",
    REFUND = "REFUND",
    CANCEL = "CANCEL",
    SALE = "SALE",
    VOID = "VOID"

