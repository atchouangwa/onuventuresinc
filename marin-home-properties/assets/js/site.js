/* Marin Home Properties — site behaviour
   Ports the interactive logic from "Marin Home Properties.dc.html": the mobile
   navigation panel, the FAQ accordion, the interest chips and the contact form.
   Everything degrades gracefully: with JavaScript off the panel is unreachable
   but the desktop navigation, every answer in the FAQ and the form itself all
   remain in the document. */

(function () {
  'use strict';

  /* -- Mobile navigation panel ------------------------------------------- */

  var burger = document.querySelector('[data-nav-toggle]');
  var panel = document.querySelector('[data-nav-panel]');

  function setNav(open) {
    document.body.classList.toggle('nav-open', open);
    if (burger) burger.setAttribute('aria-expanded', String(open));
    if (panel) panel.setAttribute('aria-hidden', String(!open));
  }

  if (burger && panel) {
    setNav(false);
    burger.addEventListener('click', function () {
      setNav(!document.body.classList.contains('nav-open'));
    });
    panel.querySelectorAll('[data-nav-close], a').forEach(function (el) {
      el.addEventListener('click', function () { setNav(false); });
    });
    document.addEventListener('keydown', function (e) {
      if (e.key === 'Escape') setNav(false);
    });
    // The desktop navigation returns at 1024px; never leave the panel stuck open.
    var wide = window.matchMedia('(min-width: 1024px)');
    var onWide = function (e) { if (e.matches) setNav(false); };
    if (wide.addEventListener) wide.addEventListener('change', onWide);
    else if (wide.addListener) wide.addListener(onWide);
  }

  /* -- FAQ accordion ------------------------------------------------------ */

  var faqButtons = Array.prototype.slice.call(document.querySelectorAll('[data-faq-q]'));

  faqButtons.forEach(function (btn) {
    btn.addEventListener('click', function () {
      var open = btn.getAttribute('aria-expanded') === 'true';
      faqButtons.forEach(function (other) {
        var answer = document.getElementById(other.getAttribute('aria-controls'));
        var next = other === btn && !open;
        other.setAttribute('aria-expanded', String(next));
        var sign = other.querySelector('[data-faq-sign]');
        if (sign) sign.textContent = next ? '−' : '+';
        if (answer) answer.hidden = !next;
      });
    });
  });

  /* -- Contact form ------------------------------------------------------- */

  var form = document.querySelector('[data-contact-form]');
  if (!form) return;

  var sent = document.querySelector('[data-contact-sent]');
  var errorBox = form.querySelector('[data-form-error]');
  var interest = form.querySelector('[data-interest]');
  var chips = Array.prototype.slice.call(form.querySelectorAll('[data-chip]'));

  chips.forEach(function (chip) {
    chip.addEventListener('click', function () {
      chips.forEach(function (other) {
        other.setAttribute('aria-pressed', String(other === chip));
      });
      if (interest) interest.value = chip.textContent.trim();
    });
  });

  function showError(message) {
    if (!errorBox) return;
    errorBox.textContent = message || '';
    errorBox.hidden = !message;
  }

  form.addEventListener('submit', function (e) {
    e.preventDefault();
    var data = new FormData(form);
    var first = String(data.get('first') || '').trim();
    var last = String(data.get('last') || '').trim();
    var email = String(data.get('email') || '').trim();

    if (!first || !last || !/^[^@\s]+@[^@\s]+\.[^@\s]+$/.test(email)) {
      showError('Please add your name and a valid email address.');
      return;
    }
    showError('');

    /* The canvas ships this as a mockup: the enquiry is acknowledged in the
       page and nothing is transmitted. To deliver it for real, POST `data` to
       a serverless handler here and only reveal the confirmation once it
       resolves. See README.md. */
    form.hidden = true;
    if (sent) {
      sent.hidden = false;
      var heading = sent.querySelector('[data-sent-title]');
      if (heading) heading.focus();
    }
  });

  var again = document.querySelector('[data-send-another]');
  if (again) {
    again.addEventListener('click', function () {
      form.reset();
      chips.forEach(function (chip, i) { chip.setAttribute('aria-pressed', String(i === 0)); });
      if (interest && chips.length) interest.value = chips[0].textContent.trim();
      showError('');
      if (sent) sent.hidden = true;
      form.hidden = false;
      var firstField = form.querySelector('input');
      if (firstField) firstField.focus();
    });
  }
})();
