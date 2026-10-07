const money = value => `$${Number(value).toFixed(2)}`;
const cartDrawer = document.querySelector('#cart-drawer');
const overlay = document.querySelector('#overlay');

async function request(path, options = {}) {
  const response = await fetch(path, { headers: {'Content-Type': 'application/json'}, ...options });
  const data = await response.json();
  if (!response.ok) throw new Error(data.error || 'Something went wrong.');
  return data;
}

function showCart(data) {
  document.querySelector('#cart-count').textContent = data.count;
  document.querySelector('#drawer-count').textContent = `(${data.count})`;
  document.querySelector('#cart-total').textContent = money(data.total);
  const target = document.querySelector('#cart-items');
  if (!data.items.length) {
    target.innerHTML = '<p class="empty-cart">Your bag is waiting for something good.</p>';
    return;
  }
  target.innerHTML = data.items.map(item => `
    <div class="cart-row">
      <img src="${item.image}" alt="${item.name}">
      <div><h3>${item.name}</h3><p>${money(item.price)}</p>
        <div class="qty-controls"><button data-id="${item.id}" data-qty="${item.quantity - 1}" aria-label="Decrease quantity">−</button><span>${item.quantity}</span><button data-id="${item.id}" data-qty="${item.quantity + 1}" aria-label="Increase quantity">+</button></div>
      </div><span class="cart-price">${money(item.line_total)}</span>
    </div>`).join('');
}

async function refreshCart() { showCart(await request('/api/cart')); }
function openCart() { cartDrawer.classList.add('open'); overlay.classList.add('open'); cartDrawer.setAttribute('aria-hidden','false'); }
function closeCart() { cartDrawer.classList.remove('open'); overlay.classList.remove('open'); cartDrawer.setAttribute('aria-hidden','true'); }

document.querySelectorAll('.quick-add').forEach(button => button.addEventListener('click', async () => {
  try {
    const id = Number(button.dataset.product);
    const current = await request('/api/cart');
    const existing = current.items.find(item => item.id === id)?.quantity || 0;
    const data = await request('/api/cart', {method:'POST', body:JSON.stringify({product_id:id, quantity:Math.min(existing + 1, 20)})});
    showCart(data); openCart();
  }
  catch (error) { alert(error.message); }
}));

document.querySelector('#cart-items').addEventListener('click', async event => {
  const button = event.target.closest('button[data-id]');
  if (!button) return;
  try { showCart(await request('/api/cart', {method:'POST', body:JSON.stringify({product_id:Number(button.dataset.id), quantity:Number(button.dataset.qty)})})); }
  catch (error) { alert(error.message); }
});

document.querySelector('#filters').addEventListener('click', event => {
  const button = event.target.closest('button[data-category]');
  if (!button) return;
  document.querySelectorAll('.filter').forEach(filter => filter.classList.toggle('active', filter === button));
  document.querySelectorAll('.product-card').forEach(card => { card.classList.toggle('hidden', button.dataset.category !== 'All' && card.dataset.category !== button.dataset.category); });
});

document.querySelector('#open-cart').addEventListener('click', openCart);
document.querySelector('#close-cart').addEventListener('click', closeCart);
overlay.addEventListener('click', closeCart);
document.addEventListener('keydown', event => { if (event.key === 'Escape') closeCart(); });

document.querySelector('#checkout-form').addEventListener('submit', async event => {
  event.preventDefault();
  const message = document.querySelector('#checkout-message');
  const form = new FormData(event.currentTarget);
  const button = event.currentTarget.querySelector('button[type="submit"]');
  button.disabled = true; message.textContent = 'Placing your order…';
  try {
    const data = await request('/api/checkout', {method:'POST', body:JSON.stringify(Object.fromEntries(form.entries()))});
    message.textContent = `${data.message} Order #${data.order_id}.`;
    event.currentTarget.reset(); await refreshCart();
  } catch (error) { message.textContent = error.message; }
  finally { button.disabled = false; }
});

refreshCart().catch(() => {});
