# Master Prompt Implementation Status

This package is a clean rebuild source tree. It does not include a database, uploaded media, secrets, or Git history.

## Implemented

- Counseling-first public positioning and service disclaimer
- English and Nepali localized routing and reusable translation system
- Navy-led responsive design system
- Normalized Person / MembershipRecord registry
- Multiple memberships per person
- Numeric membership-number ordering in public search results
- Repeatable workbook import with dry-run, reconciliation, CSV reports, backups, duplicate warnings, and idempotency tests
- Required phone and consent on counseling/contact forms
- International phone input with Nepal as the local default
- Private counseling submissions and private payment evidence
- Manual payment review with logged approval/rejection and idempotent processing
- Draft/published/archived content workflow
- Public member privacy controls
- Custom 400, 403, 404, 429, 500, and maintenance pages
- CSP, HSTS production configuration, secure-cookie settings, CSRF protection, and security headers
- Sitemap, robots.txt, localized routes, and canonical metadata support
- Render build/start configuration using the real Django WSGI application
- GitHub Actions test workflow

## Requires verified organization input

The project intentionally does not invent addresses, phone numbers, registration details, leadership claims, emergency contacts, partnerships, statistics, or testimonials. Authorized administrators must enter and approve those details.

## Launch gate

Before deployment, run migrations, the full test suite, member-import dry-runs, a production database backup, bilingual content review, Cloudinary permission verification, email delivery tests, and device/browser checks.
