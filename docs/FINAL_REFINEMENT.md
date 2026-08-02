# Final client-ready refinement

This release focuses on reader clarity, responsive navigation, natural English/Nepali localization, accessibility, and official logo consistency. It does not replace or reset production data.

## Public writing

The public interface now uses short, practical wording. Reader-facing phrases such as “pathway,” “appropriate referral,” “normalized member directory,” “service boundary,” “reintegration,” and similar policy or database language were removed from public templates.

The website clearly explains:

- what MRN Ilam can help with;
- how private counseling works;
- what to check before paying;
- warning signs of unsafe job offers;
- how membership differs from counseling;
- how payment proof is reviewed;
- what information remains private;
- what to do during an urgent situation.

Verified organization facts remain sourced from Django Admin. The release does not rewrite the client’s official name, leadership, slogan, objective, commitment, registration details, address, or service area.

## Navigation and responsive behavior

The desktop navigation uses a separate row so links do not compete with the logo and organization name. At 1120 pixels and below, the site switches to a right-side mobile drawer. The drawer:

- closes after link selection;
- closes with Escape;
- closes when the background is selected;
- prevents background scrolling;
- handles keyboard focus;
- keeps the language switch inside the mobile menu;
- uses touch targets of at least approximately 44 pixels.

Layouts include mobile fallbacks for forms, filters, member records, payment details, resources, cards, pagination, and footer content. The CSS specifically supports 320-pixel screens through large desktops without intentionally shrinking navigation text to unreadable sizes.

## Accessibility

The release adds or strengthens:

- a skip-to-content link;
- semantic headings and landmarks;
- visible keyboard focus;
- connected form labels, help text, and errors;
- required-field announcements;
- polite status messages and alert summaries;
- keyboard-accessible mobile navigation;
- meaningful logo alternative text;
- sufficient touch-target sizes;
- reduced-motion behavior;
- responsive layouts intended to remain usable at 200% zoom.

## Official logo

`static/core/images/logo-official-source.jpg` is the approved existing organization seal copied from the project’s original `logo.jpeg`. It is not redesigned or recolored.

The following assets are generated from that same seal without cropping or distortion:

- navigation/footer logo;
- 48, 96, 192, and 512 pixel icons;
- Apple touch icon;
- multi-size favicon;
- web-app manifest icons;
- Open Graph image.

There are no duplicate static logical paths for these assets.

## Localization

The final public copy has corresponding Nepali translations in `locale/ne/LC_MESSAGES/django.po`, and the compiled catalogue is included. Active entries were checked for:

- duplicate message identifiers;
- empty translations;
- fuzzy translations;
- placeholder-format errors.

Run the normal Django gettext commands after future public-copy changes:

```bash
python manage.py makemessages -l ne
python manage.py compilemessages
```

## Safe legacy-copy update

Migration `core.0016_refresh_legacy_service_copy` changes only service-card rows whose titles exactly match the known old stock wording. This updates old generated copy on production while leaving custom administrator-written service cards untouched.

## Data and workflow guarantees

This refinement does not intentionally:

- delete or recreate the database;
- delete people or memberships;
- renumber membership records;
- reuse issued membership numbers;
- re-import spreadsheets;
- expose counseling attachments or payment evidence;
- change payment approval or duplicate-prevention rules;
- change public URLs;
- overwrite verified organization information.

## Required runtime verification

Run in the project virtual environment before deployment:

```bash
python manage.py check
python manage.py migrate
python manage.py makemigrations --check --dry-run
python manage.py compilemessages
python manage.py test -v 2
rm -rf staticfiles
python manage.py collectstatic --noinput
```

Then inspect the English and Nepali versions at 320, 360, 375, 390, 430, 768, 1024, 1366, and 1440 pixel widths. Complete one controlled counseling, contact, membership-application, payment-proof, and staff-review test before client handover.

## Final admin-management refinement

- Added a task-focused MRN Ilam admin dashboard with queue counts.
- Hid legacy member and resource models from the normal admin interface.
- Restricted numbering and import audit screens to superusers and made them read-only.
- Replaced technical model labels with staff-friendly labels.
- Added direct links between membership applications, payment reviews, people, and issued memberships.
- Added consistent status badges and clearer field groupings.
- Simplified counseling management and added assignment/status actions.
- Removed legacy SEO fields from the normal content editing form.
- Added the official MRN Ilam logo and favicon to Admin without changing the brand asset.
- Added a chairperson-photo preview in Admin and rendered the photo on the public About page.
- Added `docs/ADMIN_OPERATIONS_GUIDE.md` for non-technical staff.
- No legacy data, memberships, numbering history, payment records, or admin content was deleted.
