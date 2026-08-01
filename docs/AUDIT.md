# MRN Ilam production refactor audit

## Scope inspected

The audit covered the original and previously fixed project archives, all Django apps, models, migrations, forms, views, URL configurations, templates, static files, settings, management commands, dependencies, local SQLite assumptions, the two membership workbooks, and the Phakphokthum committee DOCX.

## Initial architecture

- `core`: homepage content, organization information, general contact submissions, and online membership applications.
- `members`: one database row per membership, searchable public registry, Excel imports.
- `payments`: manual QR proof, staff approval, and automatic public-member creation.
- `blog`: homepage notices with no full publication workflow.
- project settings: bilingual routes, PostgreSQL/SQLite, WhiteNoise, Cloudinary, Render.

## Critical findings

1. **Person and membership were conflated.** A human who held two memberships appeared as two unrelated people, and identity could not be reviewed safely.
2. **The old reset import script deleted every member.** It was removed. Production imports now have no delete-by-absence behavior.
3. **Imports were tied to specific local files and weak duplicate assumptions.** The new importer accepts a path, detects sheets/headers, supports dry runs and reports, and records every processed row.
4. **Same-name merging was unsafe.** The new identity resolver never merges by name alone. Exact phone plus a strong name match may link memberships; contradictions create review flags.
5. **A public admin-creation endpoint previously existed.** It was removed. Admin creation now uses a private environment-backed management command.
6. **Payment URLs used sequential identifiers.** Signed expiring links and UUID audit identifiers are now used.
7. **Payment approval could fail against a removed member field.** Approval now updates the legacy row and normalized membership in one transaction.
8. **Duplicate open payment proofs were possible.** A conditional database constraint and transactional view prevent them.
9. **Payment and counseling uploads could be exposed through direct storage links.** Public pages never link to them; authorized staff access uses protected admin streaming endpoints.
10. **Contact was not counseling-first and did not require a phone.** A dedicated private counseling workflow now requires a normalized Nepal phone and explicit consent.
11. **Email notifications risked carrying personal content.** Staff notifications now contain a generic record reference rather than full messages or phone numbers.
12. **The homepage language and calls to action could resemble a service/agency portal.** The public positioning now emphasizes counseling, awareness, verification, and official referrals, with a clear non-agency statement.
13. **Tailwind was loaded from a browser CDN.** It was replaced with small first-party CSS and minimal JavaScript for CSP, performance, and low bandwidth.
14. **Article records had no draft/published/archived workflow, slugs, summaries, or detail pages.** These were added without deleting existing articles.
15. **Official contacts and resources were hardcoded or unreviewed.** They are now admin-managed with active and last-reviewed fields.
16. **The uploaded local SQLite database was not a reliable image of production.** It lacked current member/payment tables. Production PostgreSQL must be backed up and reconciled before deployment.
17. **The municipality workbook contains a footer row (`आजिवन सदस्य - 54`) that looks like a name.** It is now classified as non-data rather than imported as a fake person.

## Removed or retired

- Public `setup-admin-user` route and hardcoded credentials.
- Destructive `reset_import_members_unmerged.py`.
- Unused duplicate payment template.
- Stale monolithic homepage template that exposed legacy team contact details.
- Raw SVG rendering with `|safe`; the legacy field remains for preservation but is not rendered.
- Automatic membership import during deployment.
- `makemigrations` in the Render build command.

## Data risks that remain outside repository verification

- The exact row count and constraints in the live Neon/PostgreSQL database were not available.
- Cloudinary delivery settings and whether the account supports authenticated/private asset delivery were not available.
- Real staff roles, official contacts, service hours, registration information, emergency contacts, payment purpose, and retention period require organization approval.
- Automatically romanized English personal names require human review; personal names are not translated by the public UI.
