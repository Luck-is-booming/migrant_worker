(function () {
  const button = document.querySelector('[data-nav-toggle]');
  const nav = document.querySelector('[data-site-nav]');
  const scrim = document.querySelector('[data-nav-scrim]');
  const mobileQuery = window.matchMedia('(max-width: 1120px)');

  if (!button || !nav || !scrim) return;

  const focusableSelector = 'a[href], button:not([disabled]), input:not([disabled]), select:not([disabled]), textarea:not([disabled]), [tabindex]:not([tabindex="-1"])';

  function isOpen() {
    return nav.classList.contains('is-open');
  }

  function setMobileState() {
    if (mobileQuery.matches) {
      if (!isOpen()) nav.inert = true;
    } else {
      nav.inert = false;
      closeMenu(false);
    }
  }

  function openMenu() {
    nav.inert = false;
    nav.classList.add('is-open');
    scrim.classList.add('is-open');
    document.body.classList.add('nav-open');
    button.setAttribute('aria-expanded', 'true');
    scrim.setAttribute('tabindex', '0');
    const firstLink = nav.querySelector('a[href]');
    if (firstLink) firstLink.focus();
  }

  function closeMenu(returnFocus) {
    nav.classList.remove('is-open');
    scrim.classList.remove('is-open');
    document.body.classList.remove('nav-open');
    button.setAttribute('aria-expanded', 'false');
    scrim.setAttribute('tabindex', '-1');
    if (mobileQuery.matches) nav.inert = true;
    if (returnFocus) button.focus();
  }

  button.addEventListener('click', function () {
    if (isOpen()) closeMenu(true);
    else openMenu();
  });

  scrim.addEventListener('click', function () {
    closeMenu(true);
  });

  nav.addEventListener('click', function (event) {
    if (event.target.closest('a[href]') && mobileQuery.matches) closeMenu(false);
  });

  document.addEventListener('keydown', function (event) {
    if (!isOpen()) return;

    if (event.key === 'Escape') {
      event.preventDefault();
      closeMenu(true);
      return;
    }

    if (event.key !== 'Tab') return;

    const items = [button].concat(Array.from(nav.querySelectorAll(focusableSelector)));
    if (!items.length) return;
    const first = items[0];
    const last = items[items.length - 1];

    if (event.shiftKey && document.activeElement === first) {
      event.preventDefault();
      last.focus();
    } else if (!event.shiftKey && document.activeElement === last) {
      event.preventDefault();
      first.focus();
    }
  });

  if (typeof mobileQuery.addEventListener === 'function') {
    mobileQuery.addEventListener('change', setMobileState);
  } else {
    mobileQuery.addListener(setMobileState);
  }

  setMobileState();
})();
