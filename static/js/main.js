// Initialize Swiper
document.addEventListener('DOMContentLoaded', function() {
    if (document.querySelector('.banner-swiper')) {
        new Swiper('.banner-swiper', { 
            loop: true, 
            autoplay: { delay: 5000 }, 
            navigation: { nextEl: '.swiper-button-next', prevEl: '.swiper-button-prev' }, 
            pagination: { el: '.swiper-pagination', clickable: true } 
        });
    }
    
    // Scroll reveal
    const revealElements = document.querySelectorAll('.scroll-reveal');
    function checkReveal() {
        revealElements.forEach(el => {
            if (el.getBoundingClientRect().top < window.innerHeight - 100) {
                el.classList.add('revealed');
            }
        });
    }
    window.addEventListener('scroll', checkReveal);
    checkReveal();
    
    // Newsletter subscription
    const subscribeBtn = document.querySelector('.newsletter-input button');
    if (subscribeBtn) {
        subscribeBtn.addEventListener('click', function() {
            const email = document.querySelector('.newsletter-input input').value;
            if (email) {
                alert('Thank you for subscribing! You will receive our wellness updates.');
                document.querySelector('.newsletter-input input').value = '';
            } else {
                alert('Please enter your email address.');
            }
        });
    }
});