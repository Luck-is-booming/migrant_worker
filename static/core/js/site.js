(function () {
  const button = document.querySelector('[data-nav-toggle]');
  const nav = document.querySelector('[data-site-nav]');
  const languageSelect = document.querySelector('[data-language-select]');
  if (languageSelect) {
    languageSelect.addEventListener('change', function () {
      languageSelect.form.submit();
    });
  }
  if (!button || !nav) return;
  button.addEventListener('click', function () {
    const open = nav.classList.toggle('is-open');
    button.setAttribute('aria-expanded', String(open));
  });
  document.addEventListener('keydown', function (event) {
    if (event.key === 'Escape' && nav.classList.contains('is-open')) {
      nav.classList.remove('is-open');
      button.setAttribute('aria-expanded', 'false');
      button.focus();
    }
  });
})();
