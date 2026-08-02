(function () {
  const button = document.querySelector('[data-nav-toggle]');
  const nav = document.querySelector('[data-site-nav]');
  if (!button || !nav) return;

  function closeMenu(returnFocus) {
    nav.classList.remove('is-open');
    button.setAttribute('aria-expanded', 'false');
    if (returnFocus) button.focus();
  }

  button.addEventListener('click', function () {
    const open = nav.classList.toggle('is-open');
    button.setAttribute('aria-expanded', String(open));
  });

  nav.addEventListener('click', function (event) {
    if (event.target.closest('a')) closeMenu(false);
  });

  document.addEventListener('keydown', function (event) {
    if (event.key === 'Escape' && nav.classList.contains('is-open')) closeMenu(true);
  });

  window.addEventListener('resize', function () {
    if (window.innerWidth > 960) closeMenu(false);
  });
})();
