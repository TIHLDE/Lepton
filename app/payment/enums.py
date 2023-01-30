from enum import Enum
from enumchoicefield import ChoiceEnum

class OrderStatus(ChoiceEnum):
    INITIATE = "INITIATE",
    RESERVE = "RESERVE",
    CAPTURE = "CAPTURE",
    REFUND = "REFUND",
    CANCEL = "CANCEL",
    SALE = "SALE",
    VOID = "VOID"

