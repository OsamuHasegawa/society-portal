from enum import Enum


class PaymentStatus(Enum):

    UNCONFIRMED = '振込未確認'
    CONFIRMED = '振込確認済み'
    OVER = '過剰'
    SHORT = '不足'


