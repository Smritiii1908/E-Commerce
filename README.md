# North & Co. demo shop

A small Python/Flask ecommerce starter with a responsive storefront, real product photos, category filters, a session-based shopping bag, and SQLite order storage.

## Run locally

Python 3.10 or later is recommended.

```powershell
cd shopwave
py -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
$env:SHOP_SECRET_KEY = "replace-this-with-a-long-random-secret"
py app.py
```

Then open http://127.0.0.1:5000. The database `shop.db` is created automatically when the app starts. Product photos load from Unsplash, so an internet connection is needed to display them.

## What works

- Flask serves the page and JSON endpoints.
- Add items to the bag, adjust quantities, and remove items by setting quantity to zero.
- Checkout validates customer details, saves an order in SQLite, and clears the bag.
- Browse products by category on desktop or mobile.

This starter records orders but does not charge customers. For a real shop, connect a payment processor, use production-grade secret management, add CSRF protection and inventory management, and deploy behind HTTPS with a production WSGI server. The default development secret is only suitable for local experimentation.
