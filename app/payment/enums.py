from django.db.models import TextChoices


class OrderStatus(TextChoices):
    INITIATE = "INITIATE"
    RESERVED = "RESERVED"
    CAPTURE = "CAPTURE"
    REFUND = "REFUND"
    CANCEL = "CANCEL"
    SALE = "SALE"
    VOID = "VOID"
