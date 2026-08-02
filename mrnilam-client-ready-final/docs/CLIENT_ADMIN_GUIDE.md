# Client administration guide

## Staff accounts and roles

Create a separate staff account for each person and assign the smallest suitable group:

- **Content Editor**: organization text, services, resources, FAQ, leadership and articles.
- **Membership Manager**: people, memberships, categories/units, duplicate review and import history.
- **Counseling Staff**: private requests, assignment, notes and contact attempts.
- **Payment Reviewer**: private proof review and approval/rejection.
- **Administrator**: full control; reserve for trusted technical/organizational leadership.

Never share the superuser password.

## Organization information

Open **Core → Organization Information**. Enter only verified identity, registration, authority, establishment date, service area, contact, address, hours, objective, commitment, disclaimer and chairperson content. Public pages use line breaks safely; HTML is not required.

## Leadership

Open **Core → Team Members**. Fill both Nepali and English names/designations and both address versions. Phone/email are internal unless a future approved template explicitly publishes them.

The district committee spreadsheet can be imported as a draft:

```bash
python manage.py import_district_executive_committee --dry-run
```

Review English names and addresses before publishing.

## News, notices and programs

Open **Blog → Articles**:

- Draft content is never public.
- Choose Article, Notice, Safety alert, Event or Counseling update.
- Events appear under Programs.
- Add both language versions.
- Add image descriptions for accessibility.
- Use an expiry time for time-sensitive notices; expired items hide automatically without deletion.

## Official resources

Run `python manage.py seed_launch_content` once for conservative official government links and FAQ starters, then review dates and descriptions. Admin edits are never overwritten by rerunning the command.

## Counseling

Private counseling requests are visible only to authorized staff. Assign a request, update status, record a concise internal summary, add notes/contact attempts, and close it when complete. Do not copy sensitive data into external spreadsheets or personal messaging accounts without organizational authorization.

## Membership registry

- A Person can have several memberships.
- Do not create a second Person merely because the person needs a second category.
- Membership numbers become read-only once issued.
- Use **Archive** instead of delete.
- Resolve potential duplicates only after reviewing evidence.
- Public visibility is controlled separately for the person and membership.

## Payment setup

Open **Core → Membership payment settings**:

1. Enter approved General and Life fees.
2. Enter the exact verified recipient.
3. Upload the official QR.
4. Add bilingual instructions/account details.
5. Scan the QR and confirm the recipient before enabling.

The website will not accept applications until the configuration is complete and enabled.

## Payment review

Open **Payments → Manual payments**. Compare application, amount, transaction reference and the protected screenshot. Approve only verified evidence. Enter a clear applicant-facing rejection reason before rejection; keep confidential operational notes in the separate internal note field. Repeated approval is safe and does not create another membership. New evidence is stored as authenticated Cloudinary media and opened through short-lived staff-only access.

## Routine checks

```bash
python manage.py audit_launch_readiness
python manage.py export_member_registry exports/members-YYYY-MM-DD.csv
```
