/* Onu Ventures — site behaviour
   Ports the interactive logic from "Onu Ventures Home.dc.html":
   scrolled header state, mobile menu, animated stat counters, contact form. */

(function () {
  'use strict';

  var reduceMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

  /* -- Header: scrolled state ------------------------------------------- */

  var scrolled = false;

  function syncScrolled() {
    var next = window.scrollY > 80;
    if (next !== scrolled) {
      scrolled = next;
      document.body.classList.toggle('scrolled', scrolled);
    }
  }

  window.addEventListener('scroll', syncScrolled, { passive: true });

  /* -- Mobile menu ------------------------------------------------------- */

  var toggle = document.querySelector('[data-menu-toggle]');
  var panelScroll = document.querySelector('[data-panel-scroll]');

  function setMenu(open) {
    document.body.classList.toggle('menu-open', open);
    if (toggle) toggle.setAttribute('aria-expanded', String(open));
    if (open && panelScroll) panelScroll.scrollTop = 0;
  }

  if (toggle) {
    toggle.addEventListener('click', function () {
      setMenu(!document.body.classList.contains('menu-open'));
    });
  }

  document.querySelectorAll('.mobile-panel a').forEach(function (link) {
    link.addEventListener('click', function () { setMenu(false); });
  });

  document.addEventListener('keydown', function (e) {
    if (e.key === 'Escape') setMenu(false);
  });

  // The desktop nav returns at >980px; make sure the panel never sticks open.
  var wide = window.matchMedia('(min-width: 981px)');
  var onWide = function () { setMenu(false); };
  if (wide.addEventListener) wide.addEventListener('change', onWide);
  else if (wide.addListener) wide.addListener(onWide);

  /* -- Stat counters ----------------------------------------------------- */

  /* The markup already carries the final figures, so a browser that never runs
     this block (or never fires the observer) still shows the real numbers.
     We only zero them at the moment the animation actually starts. */

  var statsSection = document.getElementById('stats');
  var stats = Array.prototype.slice.call(document.querySelectorAll('[data-count-to]'));
  var counted = false;

  function renderStats(progress) {
    stats.forEach(function (el) {
      var target = Number(el.getAttribute('data-count-to')) || 0;
      var prefix = el.getAttribute('data-prefix') || '';
      var suffix = el.getAttribute('data-suffix') || '';
      var group = el.getAttribute('data-group') === 'true';
      var n = Math.round(target * progress);
      el.textContent = prefix + (group ? n.toLocaleString('en-US') : String(n)) + suffix;
    });
  }

  function runCounters() {
    if (counted) return;
    counted = true;

    if (reduceMotion) {
      renderStats(1);
      return;
    }

    var start = performance.now();
    var duration = 1700;

    (function tick(now) {
      var k = Math.min(1, (now - start) / duration);
      // easeOutCubic
      renderStats(k >= 1 ? 1 : 1 - Math.pow(1 - k, 3));
      if (k < 1) requestAnimationFrame(tick);
    })(start);
  }

  if (stats.length && statsSection) {
    if (reduceMotion) {
      // nothing to do — the markup is already the final state
    } else if ('IntersectionObserver' in window) {
      var io = new IntersectionObserver(function (entries) {
        if (entries.some(function (entry) { return entry.isIntersecting; })) {
          io.disconnect();
          runCounters();
        }
      }, { rootMargin: '0px 0px -10% 0px' });
      io.observe(statsSection);
    } else {
      var onScrollCount = function () {
        var r = statsSection.getBoundingClientRect();
        if (r.top < window.innerHeight * 0.9 && r.bottom > 0) {
          window.removeEventListener('scroll', onScrollCount);
          runCounters();
        }
      };
      window.addEventListener('scroll', onScrollCount, { passive: true });
      onScrollCount();
    }
  }

  /* -- Contact form ------------------------------------------------------ */

  var form = document.querySelector('[data-contact-form]');

  if (form) {
    var button = form.querySelector('[data-submit]');
    var status = form.querySelector('[data-form-status]');
    var state = 'idle';

    form.addEventListener('submit', function (e) {
      e.preventDefault();
      if (state === 'sending' || state === 'sent') return;

      if (!form.checkValidity()) {
        form.reportValidity();
        return;
      }

      state = 'sending';
      button.textContent = 'Sending…';
      button.disabled = true;
      status.textContent = '';
      status.classList.remove('is-error');

      var payload = {};
      new FormData(form).forEach(function (value, key) { payload[key] = value; });

      fetch('/api/contact', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      }).then(function (res) {
        if (!res.ok) throw new Error('bad status');
        form.reset();
        state = 'sent';
        button.textContent = 'Message sent';
        status.textContent = 'Thank you — we’ve received your inquiry and will reply shortly.';
      }).catch(function () {
        state = 'idle';
        button.textContent = 'Send inquiry';
        button.disabled = false;
        status.classList.add('is-error');
        status.textContent = 'Something went wrong. Please email info@onuventuresinc.com.';
      });
    });
  }

  /* -- Project overview modal (Portfolio) -------------------------------- */

  var modal = document.querySelector('[data-modal]');
  var storyEl = document.getElementById('project-stories');

  if (modal && storyEl) {
    var stories = {};
    try {
      stories = JSON.parse(storyEl.textContent);
    } catch (err) {
      stories = {};
    }

    var mImg = modal.querySelector('[data-modal-img]');
    var mCategory = modal.querySelector('[data-modal-category]');
    var mName = modal.querySelector('[data-modal-name]');
    var mMeta = modal.querySelector('[data-modal-meta]');
    var mStory = modal.querySelector('[data-modal-story]');
    var mSite = modal.querySelector('[data-modal-site]');
    var mClose = modal.querySelector('[data-modal-close]');
    var lastFocus = null;

    function openProject(key) {
      var p = stories[key];
      if (!p) return;

      mImg.src = p.img1280 || p.img;
      mImg.alt = p.alt || '';
      mCategory.textContent = p.category || '';
      mName.textContent = p.name || '';
      mMeta.textContent = [p.location, p.status].filter(Boolean).join(' · ');

      mStory.textContent = '';
      (p.story || []).forEach(function (para) {
        var el = document.createElement('p');
        el.textContent = para;
        mStory.appendChild(el);
      });

      if (p.site) {
        mSite.href = p.siteHref;
        mSite.textContent = p.site + ' \u2192';
        mSite.hidden = false;
      } else {
        mSite.hidden = true;
      }

      lastFocus = document.activeElement;
      modal.hidden = false;
      document.body.style.overflow = 'hidden';
      mClose.focus();
    }

    function closeProject() {
      if (modal.hidden) return;
      modal.hidden = true;
      document.body.style.overflow = '';
      if (lastFocus && lastFocus.focus) lastFocus.focus();
    }

    document.querySelectorAll('[data-project]').forEach(function (el) {
      el.addEventListener('click', function () {
        openProject(el.getAttribute('data-project'));
      });
      if (el.getAttribute('role') === 'button') {
        el.addEventListener('keydown', function (e) {
          if (e.key === 'Enter' || e.key === ' ') {
            e.preventDefault();
            openProject(el.getAttribute('data-project'));
          }
        });
      }
    });

    mClose.addEventListener('click', closeProject);
    modal.addEventListener('click', function (e) {
      if (!e.target.closest('[data-modal-panel]')) closeProject();
    });
    document.addEventListener('keydown', function (e) {
      if (e.key === 'Escape') closeProject();
    });
  }

  /* -- Init -------------------------------------------------------------- */

  syncScrolled();
})();
