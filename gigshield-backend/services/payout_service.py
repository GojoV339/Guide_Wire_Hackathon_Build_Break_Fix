import datetime
import random

from sqlalchemy.orm import Session

from models.payout import Payout


def generate_mock_transaction_id() -> str:
    ts = datetime.datetime.utcnow().strftime("%Y%m%d%H%M%S")
    rnd = random.randint(1000, 9999)
    return f"GS-{ts}-{rnd}"


def mark_payout_success(db: Session, payout: Payout) -> Payout:
    payout.status = "success"
    payout.paid_at = datetime.datetime.utcnow()
    if not payout.upi_transaction_id:
        payout.upi_transaction_id = generate_mock_transaction_id()
    db.add(payout)
    return payout

