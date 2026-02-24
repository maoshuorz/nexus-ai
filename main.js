/**
 * Nexus AI - 六艺智团交互脚本
 * Interactive features for pixel-style website
 */

(function() {
    'use strict';

    // ===== Configuration =====
    const CONFIG = {
        animationDuration: 300,
        scrollOffset: 80,
        revealThreshold: 0.1,
        parallaxStrength: 5
    };

    // ===== DOM Elements =====
    const elements = {
        navLinks: document.getElementById('navLinks'),
        mobileMenuBtn: document.querySelector('.mobile-menu-btn'),
        revealElements: document.querySelectorAll('.reveal'),
        heroRobots: document.querySelectorAll('.hero-robot'),
        agentCards: document.querySelectorAll('.agent-card'),
        statNumbers: document.querySelectorAll('.stat-number')
    };

    // ===== Mobile Menu =====
    function toggleMenu() {
        elements.navLinks?.classList.toggle('active');
    }

    function closeMenu() {
        elements.navLinks?.classList.remove('active');
    }

    // ===== Smooth Scroll =====
    function initSmoothScroll() {
        document.querySelectorAll('a[href^="#"]').forEach(anchor => {
            anchor.addEventListener('click', function(e) {
                e.preventDefault();
                const targetId = this.getAttribute('href');
                const target = document.querySelector(targetId);
                
                if (target) {
                    const offsetTop = target.offsetTop - CONFIG.scrollOffset;
                    window.scrollTo({
                        top: offsetTop,
                        behavior: 'smooth'
                    });
                    closeMenu();
                }
            });
        });
    }

    // ===== Scroll Reveal =====
    function initScrollReveal() {
        const observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    entry.target.classList.add('active');
                    
                    // Animate stat numbers
                    if (entry.target.querySelector('.stat-number')) {
                        animateStatNumber(entry.target.querySelector('.stat-number'));
                    }
                }
            });
        }, {
            threshold: CONFIG.revealThreshold,
            rootMargin: '0px 0px -50px 0px'
        });

        elements.revealElements.forEach(el => observer.observe(el));
    }

    // ===== Stat Number Animation =====
    function animateStatNumber(element) {
        const text = element.textContent;
        const numMatch = text.match(/[\d,]+/);
        
        if (!numMatch) return;
        
        const finalNum = parseInt(numMatch[0].replace(/,/g, ''));
        const suffix = text.replace(numMatch[0], '');
        const duration = 2000;
        const startTime = performance.now();
        
        function update(currentTime) {
            const elapsed = currentTime - startTime;
            const progress = Math.min(elapsed / duration, 1);
            
            // Easing function
            const easeOut = 1 - Math.pow(1 - progress, 3);
            const current = Math.floor(finalNum * easeOut);
            
            element.textContent = current.toLocaleString() + suffix;
            
            if (progress < 1) {
                requestAnimationFrame(update);
            }
        }
        
        requestAnimationFrame(update);
    }

    // ===== Parallax Effect =====
    function initParallax() {
        let ticking = false;
        
        document.addEventListener('mousemove', (e) => {
            if (!ticking) {
                requestAnimationFrame(() => {
                    const x = e.clientX / window.innerWidth;
                    const y = e.clientY / window.innerHeight;
                    
                    elements.heroRobots.forEach((robot, index) => {
                        const speed = (index + 1) * CONFIG.parallaxStrength;
                        const xOffset = (x - 0.5) * speed;
                        const yOffset = (y - 0.5) * speed;
                        robot.style.transform = `translate(${xOffset}px, ${yOffset}px)`;
                    });
                    
                    ticking = false;
                });
                
                ticking = true;
            }
        });
    }

    // ===== Agent Interactions =====
    function initAgentInteractions() {
        elements.agentCards.forEach(card => {
            card.addEventListener('mouseenter', function() {
                this.style.zIndex = '10';
            });
            
            card.addEventListener('mouseleave', function() {
                this.style.zIndex = '1';
            });
            
            card.addEventListener('click', function() {
                // Add click animation
                this.style.animation = 'robotSpin 0.5s ease-in-out';
                setTimeout(() => {
                    this.style.animation = '';
                }, 500);
            });
        });
    }

    // ===== Header Scroll Effect =====
    function initHeaderScroll() {
        const header = document.querySelector('header');
        let lastScroll = 0;
        
        window.addEventListener('scroll', () => {
            const currentScroll = window.pageYOffset;
            
            if (currentScroll > 100) {
                header.style.boxShadow = '0 4px 20px rgba(78, 205, 196, 0.3)';
            } else {
                header.style.boxShadow = '0 0 20px rgba(78, 205, 196, 0.5)';
            }
            
            lastScroll = currentScroll;
        });
    }

    // ===== Easter Egg =====
    function initEasterEgg() {
        const konami = [];
        const konamiCode = ['ArrowUp', 'ArrowUp', 'ArrowDown', 'ArrowDown', 
                           'ArrowLeft', 'ArrowRight', 'ArrowLeft', 'ArrowRight', 
                           'b', 'a'];
        
        document.addEventListener('keydown', (e) => {
            konami.push(e.key);
            konami.splice(-konamiCode.length - 1, konami.length - konamiCode.length);
            
            if (konami.join(',') === konamiCode.join(',')) {
                activateEasterEgg();
            }
        });
    }

    function activateEasterEgg() {
        document.body.style.filter = 'hue-rotate(180deg)';
        
        // Show toast
        const toast = document.createElement('div');
        toast.textContent = '🎮 像素模式已激活！';
        toast.style.cssText = `
            position: fixed;
            bottom: 20px;
            right: 20px;
            background: var(--pink);
            color: var(--dark);
            padding: 1rem 2rem;
            font-family: var(--font-display);
            z-index: 9999;
            animation: slideIn 0.3s ease;
        `;
        document.body.appendChild(toast);
        
        setTimeout(() => {
            toast.remove();
            document.body.style.filter = '';
        }, 3000);
    }

    // ===== Utility Functions =====
    function showAgent(agentName) {
        const card = document.querySelector(`.agent-card.${agentName}`);
        if (card) {
            card.scrollIntoView({ behavior: 'smooth', block: 'center' });
            card.click();
        }
    }

    function debounce(func, wait) {
        let timeout;
        return function executedFunction(...args) {
            const later = () => {
                clearTimeout(timeout);
                func(...args);
            };
            clearTimeout(timeout);
            timeout = setTimeout(later, wait);
        };
    }

    // ===== Initialize =====
    function init() {
        // Expose global functions
        window.toggleMenu = toggleMenu;
        window.showAgent = showAgent;
        
        // Initialize features
        initSmoothScroll();
        initScrollReveal();
        initParallax();
        initAgentInteractions();
        initHeaderScroll();
        initEasterEgg();
        
        // Add loaded class
        document.body.classList.add('loaded');
        
        // Console easter egg
        console.log('%c🤖 六艺智团 Nexus AI', 'color: #FF6B9D; font-size: 24px; font-weight: bold;');
        console.log('%c像素智能，无限可能', 'color: #4ECDC4; font-size: 14px;');
        console.log('%c宗志 | 锦绣 | 匠心 | 墨染 | 睿思 | 明镜', 'color: #FFE66D; font-size: 12px;');
    }

    // Run on DOM ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }

})();
