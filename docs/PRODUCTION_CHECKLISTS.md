# Production, content, security, accessibility, and performance checklists

## Organization content that must be supplied or approved

- [OFFICIAL ORGANIZATION NAME IN ENGLISH]
- [OFFICIAL ORGANIZATION NAME IN NEPALI]
- [REGISTRATION NUMBER]
- [ESTABLISHED DATE]
- [OFFICIAL PHONE]
- [OFFICIAL EMAIL]
- [OFFICE ADDRESS]
- [CHAIRPERSON NAME]
- [AUTHORIZED COUNSELORS]
- [SERVICE HOURS]
- [EMERGENCY CONTACTS]
- [OFFICIAL GOVERNMENT RESOURCES]
- [PAYMENT PURPOSE]
- [PRIVACY RETENTION PERIOD]

Do not publish placeholders. Verify every official phone number and URL and populate `last_reviewed`.

## Security

- Use a long unique `SECRET_KEY`; never commit `.env`.
- Set `DEBUG=False`, production hosts, trusted HTTPS origins, and `USE_SQLITE=False` on Render.
- Keep Neon and Cloudinary credentials private and rotate any credential previously shared.
- Set `ADMIN_*` variables privately; keep `RESET_ADMIN_PASSWORD=False` except for one intentional reset.
- Do not reintroduce command-execution URLs.
- Keep counseling attachments disabled unless staff have a real need and an approved retention policy.
- Assign staff to least-privilege groups with `setup_staff_groups`.
- Review private evidence only through protected admin endpoints.
- Do not export counseling data unless the user has explicit export permission and an approved purpose.
- Review logs to ensure no request bodies, full phone numbers, OTPs, payment files, or counseling messages are logged.

## Accessibility

- Test keyboard-only navigation, menu, filters, forms, and pagination.
- Verify visible focus and skip link.
- Check heading order and form error summaries.
- Test English and Nepali with a screen reader.
- Verify contrast and 200% zoom.
- Test at 320px width with no horizontal overflow.
- Add meaningful alt text to real content images; decorative logos may use an empty alt where adjacent text identifies the brand.
- Review every data table/card with real content.
- Respect reduced-motion settings.

## Performance and low bandwidth

- Keep essential content server rendered.
- Keep first-party CSS/JS; do not restore Tailwind CDN or a SPA.
- Optimize uploaded public images before publication.
- Prefer Cloudinary transformations/responsive images for public content when configured.
- Keep counseling/payment uploads under 5 MB.
- Confirm member pages remain paginated and query counts do not grow per result.
- Confirm long-lived cache headers for hashed static assets.
- Test a cold Render start and an older mobile device.

## SEO and privacy

- Submit `/sitemap.xml` after deployment.
- Confirm `/robots.txt` disallows admin, payment, and private success URLs.
- Confirm private pages return `noindex,nofollow,noarchive`.
- Confirm drafts, archived content, private people, counseling records, and payments are absent from sitemaps.
- Replace the favicon with a clear square 96×96 or 144×144 asset if the current JPEG is not square.
- Request indexing for exact canonical URLs ending in `/`.

## Deployment verification

```bash
python manage.py check
python manage.py makemigrations --check --dry-run
python manage.py migrate
python manage.py test
python manage.py collectstatic --noinput
python manage.py setup_staff_groups
```

Then verify `/health/`, `/robots.txt`, `/sitemap.xml`, both language homepages, counseling submission, member search, article visibility, payment submission, payment review, and custom 404/500 behavior.
