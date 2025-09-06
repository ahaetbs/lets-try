# ecommerce.py
from dataclasses import dataclass
from typing import Dict, Optional
import hashlib
import uuid
import time

# --- Fake in-memory data stores ---
USERS: Dict[str, str] = {}  # email -> password_hash
PRODUCTS: Dict[str, Dict] = {
    "sku-001": {"name": "Wireless Mouse", "price": 249.90, "stock": 42},
    "sku-002": {"name": "Mechanical Keyboard", "price": 999.00, "stock": 8},
    "sku-003": {"name": "USB-C Cable", "price": 99.00, "stock": 120},
}
DISCOUNTS: Dict[str, float] = {  # code -> percent off (0..1)
    "WELCOME10": 0.10,
    "SUMMER15": 0.15,
}
ORDERS: Dict[str, Dict] = {}  # order_id -> order record


def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode("utf-8")).hexdigest()


def verify_password(password: str, password_hash: str) -> bool:
    return hash_password(password) == password_hash


def create_user(email: str, password: str) -> bool:
    if email in USERS:
        return False
    USERS[email] = hash_password(password)
    return True


def login_user(email: str, password: str) -> bool:
    ph = USERS.get(email)
    return bool(ph and verify_password(password, ph))


def list_products() -> Dict[str, Dict]:
    return PRODUCTS.copy()


def get_product(sku: str) -> Optional[Dict]:
    return PRODUCTS.get(sku)


def add_to_cart(cart: Dict[str, int], sku: str, qty: int = 1) -> None:
    if sku not in PRODUCTS:
        raise KeyError("SKU not found")
    if qty <= 0:
        raise ValueError("qty must be positive")
    available = PRODUCTS[sku]["stock"]
    if qty > available:
        raise ValueError("insufficient stock")
    cart[sku] = cart.get(sku, 0) + qty


def remove_from_cart(cart: Dict[str, int], sku: str, qty: int = 1) -> None:
    if sku not in cart:
        return
    cart[sku] -= qty
    if cart[sku] <= 0:
        del cart[sku]


def calculate_cart_total(cart: Dict[str, int]) -> float:
    total = 0.0
    for sku, qty in cart.items():
        p = PRODUCTS.get(sku)
        if not p:
            continue
        total += p["price"] * qty
    return round(total, 2)


def apply_discount_code(total: float, code: str) -> float:
    pct = DISCOUNTS.get(code, 0.0)
    return round(total * (1 - pct), 2)


def generate_order_id() -> str:
    return "ord_" + uuid.uuid4().hex[:12]


@dataclass
class PaymentResult:
    ok: bool
    tx_id: Optional[str] = None
    reason: Optional[str] = None


def charge_payment(amount: float, provider: str = "stripe") -> PaymentResult:
    if amount <= 0:
        return PaymentResult(ok=False, reason="invalid_amount")
    # fake “processing”
    time.sleep(0.01)
    return PaymentResult(ok=True, tx_id=f"{provider}_{uuid.uuid4().hex[:10]}")


def create_order(email: str, cart: Dict[str, int], total_paid: float) -> str:
    order_id = generate_order_id()
    ORDERS[order_id] = {
        "email": email,
        "items": cart.copy(),
        "total": round(total_paid, 2),
        "status": "paid",
    }
    return order_id


def get_order_status(order_id: str) -> Optional[str]:
    order = ORDERS.get(order_id)
    return order["status"] if order else None
