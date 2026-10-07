from __future__ import annotations

import os
import sqlite3
from datetime import datetime, timezone
from pathlib import Path

from flask import Flask, jsonify, render_template, request, session

BASE_DIR = Path(__file__).resolve().parent
DATABASE = BASE_DIR / "shop.db"
app = Flask(__name__)
app.secret_key = os.environ.get("SHOP_SECRET_KEY", "dev-only-change-this-secret")

# Product photography is served by Unsplash's image CDN.
PRODUCTS = [
    {"id": 1, "name": "Studio Wireless Headphones", "category": "Tech", "price": 89.00,
     "image": "https://images.unsplash.com/photo-1505740420928-5e560c06d30e?auto=format&fit=crop&w=900&q=85",
     "description": "Rich, balanced sound and all-day comfort in a clean, lightweight design."},
    {"id": 2, "name": "Everyday Leather Backpack", "category": "Accessories", "price": 119.00,
     "image": "https://images.unsplash.com/photo-1553062407-98eeb64c6a62?auto=format&fit=crop&w=900&q=85",
     "description": "A versatile carry-all with thoughtful pockets and a timeless profile."},
    {"id": 3, "name": "Minimal Ceramic Watch", "category": "Accessories", "price": 145.00,
     "image": "https://images.unsplash.com/photo-1523275335684-37898b6baf30?auto=format&fit=crop&w=900&q=85",
     "description": "A simple, elegant timepiece made for everyday wear."},
    {"id": 4, "name": "Classic Running Sneakers", "category": "Style", "price": 98.00,
     "image": "https://images.unsplash.com/photo-1542291026-7eec264c27ff?auto=format&fit=crop&w=900&q=85",
     "description": "Light cushioning and a confident pop of color for your daily miles."},
    {"id": 5, "name": "Everyday Sunglasses", "category": "Style", "price": 64.00,
     "image": "https://images.unsplash.com/photo-1511499767150-a48a237f0083?auto=format&fit=crop&w=900&q=85",
     "description": "Easy-to-wear frames with UV-protective lenses."},
    {"id": 6, "name": "Soft Knit Lounge Chair", "category": "Home", "price": 249.00,
     "image": "https://images.unsplash.com/photo-1503602642458-232111445657?auto=format&fit=crop&w=900&q=85",
     "description": "A welcoming accent chair that brings a little calm to your space."},
    {"id": 7, "name": "Glass Pour-Over Set", "category": "Home", "price": 52.00,
     "image": "https://images.unsplash.com/photo-1495474472287-4d71bcdd2085?auto=format&fit=crop&w=900&q=85",
     "description": "A considered coffee ritual, from the first pour to the last drop."},
    {"id": 8, "name": "Canvas Weekend Tote", "category": "Accessories", "price": 42.00,
     "image": "https://images.unsplash.com/photo-1590874103328-eac38a683ce7?auto=format&fit=crop&w=900&q=85",
     "description": "A roomy, durable tote for errands, work, and weekends away."},
]


def connect_db() -> sqlite3.Connection:
    db = sqlite3.connect(DATABASE)
    db.row_factory = sqlite3.Row
    return db


def init_db() -> None:
    with connect_db() as db:
        db.execute("""CREATE TABLE IF NOT EXISTS orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            customer_name TEXT NOT NULL,
            email TEXT NOT NULL,
            address TEXT NOT NULL,
            items_json TEXT NOT NULL,
            total REAL NOT NULL,
            created_at TEXT NOT NULL
        )""")


def cart_details() -> tuple[list[dict], float]:
    cart = session.get("cart", {})
    items = []
    for product in PRODUCTS:
        quantity = int(cart.get(str(product["id"]), 0))
        if quantity > 0:
            items.append({**product, "quantity": quantity, "line_total": round(product["price"] * quantity, 2)})
    return items, round(sum(item["line_total"] for item in items), 2)


@app.get("/")
def home():
    return render_template("index.html", products=PRODUCTS)


@app.get("/api/cart")
def get_cart():
    items, total = cart_details()
    return jsonify(items=items, total=total, count=sum(item["quantity"] for item in items))


@app.post("/api/cart")
def update_cart():
    payload = request.get_json(silent=True) or {}
    try:
        product_id = int(payload.get("product_id", 0))
        quantity = int(payload.get("quantity", 1))
    except (TypeError, ValueError):
        return jsonify(error="Product and quantity must be whole numbers."), 400
    if not any(product["id"] == product_id for product in PRODUCTS):
        return jsonify(error="That product was not found."), 404
    if not 0 <= quantity <= 20:
        return jsonify(error="Quantity must be between 0 and 20."), 400
    cart = session.get("cart", {})
    if quantity == 0:
        cart.pop(str(product_id), None)
    else:
        cart[str(product_id)] = quantity
    session["cart"] = cart
    items, total = cart_details()
    return jsonify(items=items, total=total, count=sum(item["quantity"] for item in items))


@app.post("/api/checkout")
def checkout():
    payload = request.get_json(silent=True) or {}
    name = str(payload.get("name", "")).strip()[:100]
    email = str(payload.get("email", "")).strip()[:200]
    address = str(payload.get("address", "")).strip()[:300]
    if not name or "@" not in email or not address:
        return jsonify(error="Enter your name, a valid email, and a delivery address."), 400
    items, total = cart_details()
    if not items:
        return jsonify(error="Your cart is empty."), 400
    import json
    with connect_db() as db:
        cursor = db.execute(
            "INSERT INTO orders (customer_name,email,address,items_json,total,created_at) VALUES (?,?,?,?,?,?)",
            (name, email, address, json.dumps(items), total, datetime.now(timezone.utc).isoformat()),
        )
        order_id = cursor.lastrowid
    session["cart"] = {}
    return jsonify(message=f"Thanks, {name}! Your order has been placed.", order_id=order_id, total=total), 201


init_db()

if __name__ == "__main__":
    app.run(debug=os.environ.get("FLASK_DEBUG") == "1")
