from enum import Enum
from enumchoicefield import ChoiceEnum

class OrderStatus(ChoiceEnum):
    INITIATE = "INITIATE",
    RESERVE = "RESERVE",
    CAPTURE = "CAPTURE",
    REFUND = "REFUND",
    CANCEL = "CANCEL",
    SALE = "SALE",
<<<<<<< HEAD
    VOID = "VOID"

=======
    VOID = "VOID"
>>>>>>> 4255020 (added Order model, view and serializer)
