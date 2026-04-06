// ======================== PRODUCT DATABASE (EASILY EDITABLE) ========================
const products = [
  {
    id: 1,
    name: "Rosehip & Saffron Radiance Serum",
    price: 1899,
    desc: "Brightening serum with Vitamin C, Rosehip oil & saffron extract. Fades dark spots, boosts glow.",
    image: "https://images.unsplash.com/photo-1608248543803-ba4f8c70ae0b?w=500&auto=format",
    category: "Face",
    tags: ["Vitamin C", "Glow"]
  },
  {
    id: 2,
    name: "Ashwagandha & Reishi Calm Balm",
    price: 1599,
    desc: "Adaptogenic body butter infused with Ashwagandha, Reishi, Shea butter. Soothes stress, melts into skin.",
    image: "https://images.unsplash.com/photo-1600857544200-b2f666a9a2ec?w=500&auto=format",
    category: "Body",
    tags: ["Adaptogen", "Relax"]
  },
  {
    id: 3,
    name: "Berberis Aquifolium Skin Tincture",
    price: 899,
    desc: "Classic homeopathic remedy for skin clarity, detox & acne-prone skin. Alcohol-free formula.",
    image: "https://images.unsplash.com/photo-1584308666744-00d9969f4aef?w=500&auto=format",
    category: "Medicines",
    tags: ["Homeopathy", "Detox"]
  },
  {
    id: 4,
    name: "Brahmi & Amla Strength Hair Oil",
    price: 1249,
    desc: "Ayurvedic blend reduces hair fall, nourishes scalp, promotes thickness. Warm before use.",
    image: "https://images.unsplash.com/photo-1608248597279-f99d160bfcbc?w=500&auto=format",
    category: "Hair",
    tags: ["Hair Growth", "Ayurveda"]
  },
  {
    id: 5,
    name: "Calendula & Neem Clarifying Face Wash",
    price: 699,
    desc: "Gentle foaming wash with Neem, Calendula, Aloe. Balances oil, reduces inflammation.",
    image: "https://images.unsplash.com/photo-1556228720-195a672e8a03?w=500&auto=format",
    category: "Face",
    tags: ["Acne", "Purifying"]
  },
  {
    id: 6,
    name: "Moringa & Tamanu Silk Body Oil",
    price: 1499,
    desc: "Fast-absorbing dry oil for radiant, dewy skin. Packed with antioxidants & essential fatty acids.",
    image: "https://images.unsplash.com/photo-1611085583191-a3b181a88401?w=500&auto=format",
    category: "Body",
    tags: ["Glow", "Dry Oil"]
  },
  {
    id: 7,
    name: "Echinacea Immune Boost Drops",
    price: 1099,
    desc: "Herbal homeopathic tincture to strengthen natural defenses. Alcohol-free, organic echinacea.",
    image: "https://images.unsplash.com/photo-1587854692152-cbe660dbde88?w=500&auto=format",
    category: "Medicines",
    tags: ["Immune", "Herbal"]
  },
  {
    id: 8,
    name: "Bhringraj & Hibiscus Hair Mask",
    price: 799,
    desc: "Deep conditioning mask repairs split ends, adds shine, reduces premature greying.",
    image: "https://images.unsplash.com/photo-1608248543803-ba4f8c70ae0b?w=500&auto=format",
    category: "Hair",
    tags: ["Mask", "Repair"]
  }
];

// ======================== CART MANAGEMENT ========================
let cart = JSON.parse(localStorage.getItem('drnaturals_cart')) || [];

function saveCart() {
  localStorage.setItem('drnaturals_cart', JSON.stringify(cart));
  updateCartUI();
}

function updateCartUI() {
  const count = cart.reduce((sum, item) => sum + item.quantity, 0);
  const badge = document.getElementById('cartCountBadge');
  if (badge) badge.innerText = count;
  renderCartModal();
}

function addToCart(productId, quantity = 1) {
  const product = products.find(p => p.id === productId);
  if (!product) return;
  const existing = cart.find(item => item.id === productId);
  if (existing) existing.quantity += quantity;
  else cart.push({ id: product.id, name: product.name, price: product.price, quantity: quantity, image: product.image });
  saveCart();
  showToast(`${product.name} added to cart!`);
}

function removeCartItem(id) {
  cart = cart.filter(item => item.id !== id);
  saveCart();
}

function updateQuantity(id, newQty) {
  if (newQty <= 0) removeCartItem(id);
  else {
    const item = cart.find(i => i.id === id);
    if (item) item.quantity = newQty;
    saveCart();
  }
}

function renderCartModal() {
  const container = document.getElementById('cartItemsList');
  const totalSpan = document.getElementById('cartTotal');
  if (!container) return;
  if (cart.length === 0) {
    container.innerHTML = '<p>Your cart is empty, dear soul.</p>';
    if (totalSpan) totalSpan.innerHTML = 'Total: ₹0';
    return;
  }
  let html = '';
  let total = 0;
  cart.forEach(item => {
    total += item.price * item.quantity;
    html += `
      <div class="cart-item">
        <div>
          <strong>${item.name}</strong><br>
          ₹${item.price} x ${item.quantity}
        </div>
        <div>
          <button class="qty-minus" data-id="${item.id}">-</button>
          <span>${item.quantity}</span>
          <button class="qty-plus" data-id="${item.id}">+</button>
          <button class="remove-item" data-id="${item.id}" style="background:none; border:none; color:#b95f2e;"><i class="fas fa-trash-alt"></i></button>
        </div>
      </div>
    `;
  });
  container.innerHTML = html;
  if (totalSpan) totalSpan.innerHTML = `Total: ₹${total}`;

  // Attach event listeners
  document.querySelectorAll('.qty-minus').forEach(btn => {
    btn.addEventListener('click', (e) => {
      const id = parseInt(btn.dataset.id);
      const item = cart.find(i => i.id === id);
      if (item) updateQuantity(id, item.quantity - 1);
    });
  });
  document.querySelectorAll('.qty-plus').forEach(btn => {
    btn.addEventListener('click', (e) => {
      const id = parseInt(btn.dataset.id);
      const item = cart.find(i => i.id === id);
      if (item) updateQuantity(id, item.quantity + 1);
    });
  });
  document.querySelectorAll('.remove-item').forEach(btn => {
    btn.addEventListener('click', (e) => {
      removeCartItem(parseInt(btn.dataset.id));
    });
  });
}

function showToast(msg) {
  const toast = document.createElement('div');
  toast.innerText = msg;
  toast.style.position = 'fixed';
  toast.style.bottom = '20px';
  toast.style.left = '20px';
  toast.style.backgroundColor = '#2F4D2D';
  toast.style.color = 'white';
  toast.style.padding = '10px 20px';
  toast.style.borderRadius = '40px';
  toast.style.zIndex = '2000';
  document.body.appendChild(toast);
  setTimeout(() => toast.remove(), 2000);
}

// ======================== CART MODAL CONTROLS ========================
document.addEventListener('DOMContentLoaded', () => {
  const cartModal = document.getElementById('cartModal');
  const cartIcon = document.getElementById('cartIconBtn');
  const closeBtn = document.getElementById('closeCartBtn');
  const checkoutBtn = document.getElementById('checkoutBtn');

  if (cartIcon) {
    cartIcon.onclick = () => {
      renderCartModal();
      if (cartModal) cartModal.style.display = 'flex';
    };
  }
  if (closeBtn) closeBtn.onclick = () => { if (cartModal) cartModal.style.display = 'none'; };
  if (checkoutBtn) {
    checkoutBtn.onclick = () => {
      if (cart.length === 0) {
        alert('Your cart is empty.');
        return;
      }
      alert('✨ Order placed successfully! (Demo) ✨\nThank you for shopping at Dr Naturals.');
      cart = [];
      saveCart();
      if (cartModal) cartModal.style.display = 'none';
    };
  }
  window.onclick = (e) => { if (e.target === cartModal) cartModal.style.display = 'none'; };
  updateCartUI();
});