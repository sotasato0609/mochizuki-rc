/* =========================================
   望月リソルゴルフクラブ LP
   main.js - ナビ・スクロール・アニメーション
   v1.1
   ========================================= */

(function () {
  'use strict';

  /* ---- Nav: scroll behaviour ---- */
  var nav = document.querySelector('.global-nav');
  function onScroll() {
    if (window.scrollY > 60) {
      nav.classList.add('scrolled');
    } else {
      nav.classList.remove('scrolled');
    }
  }
  window.addEventListener('scroll', onScroll, { passive: true });
  onScroll();

  /* ---- Hamburger menu ---- */
  var hamburger = document.getElementById('hamburger');
  var navLinks  = document.getElementById('nav-links');

  hamburger.addEventListener('click', function () {
    var isOpen = navLinks.classList.toggle('open');
    hamburger.classList.toggle('active');
    hamburger.setAttribute('aria-expanded', isOpen ? 'true' : 'false');
    hamburger.setAttribute(
      'aria-label',
      isOpen ? 'メニューを閉じる' : 'メニューを開く'
    );
  });

  // Close on nav link click
  navLinks.querySelectorAll('.nav-link').forEach(function (link) {
    link.addEventListener('click', function () {
      hamburger.classList.remove('active');
      navLinks.classList.remove('open');
      hamburger.setAttribute('aria-expanded', 'false');
      hamburger.setAttribute('aria-label', 'メニューを開く');
    });
  });

  /* ---- Fade-in: Intersection Observer ---- */
  var fadeEls = document.querySelectorAll('.fade-in');
  if ('IntersectionObserver' in window) {
    var fadeObserver = new IntersectionObserver(function (entries) {
      entries.forEach(function (entry) {
        if (entry.isIntersecting) {
          entry.target.classList.add('visible');
          fadeObserver.unobserve(entry.target);
        }
      });
    }, { threshold: 0.12, rootMargin: '0px 0px -40px 0px' });

    fadeEls.forEach(function (el, i) {
      // Stagger delay for grid children (numbers / benefits)
      var parent = el.parentElement;
      if (parent && (parent.classList.contains('numbers-grid') || parent.classList.contains('benefit-grid'))) {
        var siblings = Array.from(parent.querySelectorAll('.fade-in'));
        var idx = siblings.indexOf(el);
        if (idx > -1) {
          el.style.transitionDelay = (idx * 0.12) + 's';
        }
      }
      fadeObserver.observe(el);
    });
  } else {
    // Fallback: show all immediately
    fadeEls.forEach(function (el) { el.classList.add('visible'); });
  }

  /* ---- Counter animation ---- */
  function animateCounter(el) {
    var target   = parseInt(el.getAttribute('data-target'), 10);
    var duration = 2000;
    var startTime = null;
    function easeOutCubic(t) { return 1 - Math.pow(1 - t, 3); }
    function tick(timestamp) {
      if (!startTime) startTime = timestamp;
      var elapsed  = timestamp - startTime;
      var progress = Math.min(elapsed / duration, 1);
      el.textContent = Math.floor(easeOutCubic(progress) * target).toLocaleString('ja-JP');
      if (progress < 1) requestAnimationFrame(tick);
      else el.textContent = target.toLocaleString('ja-JP');
    }
    requestAnimationFrame(tick);
  }

  var counters = document.querySelectorAll('.counter');
  if (counters.length) {
    if ('IntersectionObserver' in window) {
      var counterObs = new IntersectionObserver(function (entries, o) {
        entries.forEach(function (entry) {
          if (entry.isIntersecting) { animateCounter(entry.target); o.unobserve(entry.target); }
        });
      }, { threshold: 0.2, rootMargin: '0px 0px -20px 0px' });
      counters.forEach(function (c) { counterObs.observe(c); });
    } else {
      counters.forEach(function (c) {
        c.textContent = parseInt(c.getAttribute('data-target'), 10).toLocaleString('ja-JP');
      });
    }
  }

  /* ---- Smooth scroll offset for fixed nav ---- */
  document.querySelectorAll('a[href^="#"]').forEach(function (anchor) {
    anchor.addEventListener('click', function (e) {
      var targetId = this.getAttribute('href');
      if (targetId === '#' || targetId === '#top') {
        e.preventDefault();
        window.scrollTo({ top: 0, behavior: 'smooth' });
        return;
      }
      var target = document.querySelector(targetId);
      if (!target) return;
      e.preventDefault();
      var navH = parseInt(
        getComputedStyle(document.documentElement).getPropertyValue('--nav-h'),
        10
      ) || 72;
      var top = target.getBoundingClientRect().top + window.scrollY - navH;
      window.scrollTo({ top: top, behavior: 'smooth' });
    });
  });

  /* ---- Birth year/month/day selectors ---- */
  var birthY = document.getElementById('birth_y');
  var birthM = document.getElementById('birth_m');
  var birthD = document.getElementById('birth_d');

  if (birthY) {
    var currentYear = new Date().getFullYear();
    for (var y = currentYear - 20; y >= currentYear - 90; y--) {
      var opt = document.createElement('option');
      opt.value = y;
      opt.textContent = y + '年';
      birthY.appendChild(opt);
    }
  }
  if (birthM) {
    for (var m = 1; m <= 12; m++) {
      var opt2 = document.createElement('option');
      opt2.value = m;
      opt2.textContent = m + '月';
      birthM.appendChild(opt2);
    }
  }
  if (birthD) {
    for (var d = 1; d <= 31; d++) {
      var opt3 = document.createElement('option');
      opt3.value = d;
      opt3.textContent = d + '日';
      birthD.appendChild(opt3);
    }
  }

  /* ---- BudouX: 日本語テキストの自然な単語区切り改行 ---- */
  if (typeof budouXJa !== 'undefined' && budouXJa.Parser) {
    var parser = new budouXJa.Parser();
    var budouxSelectors = [
      '.section-ja',
      '.course-catch',
      '.course-body',
      '.benefit-title',
      '.benefit-text',
      '.hero-badge',
      '.notice-text',
      '.form-lead',
      '.trial-includes p',
      '.trial-notes li',
      '.access-route p',
      '.membership-note',
      '.membership-badge',
      '.footer-info p'
    ];
    var budouxTargets = document.querySelectorAll(budouxSelectors.join(','));
    budouxTargets.forEach(function (el) {
      parser.applyElement(el);
    });
  }

  /* ---- SP fixed CTA: hide near footer ---- */
  var spCta = document.getElementById('sp-cta');
  if (spCta) {
    function checkSpCta() {
      var footer    = document.querySelector('.footer');
      var footerTop = footer ? footer.getBoundingClientRect().top : Infinity;
      var wh        = window.innerHeight;
      if (footerTop < wh + 100) {
        spCta.style.opacity = '0';
        spCta.style.pointerEvents = 'none';
      } else {
        spCta.style.opacity = '1';
        spCta.style.pointerEvents = '';
      }
    }
    window.addEventListener('scroll', checkSpCta, { passive: true });
    checkSpCta();
  }

})();
