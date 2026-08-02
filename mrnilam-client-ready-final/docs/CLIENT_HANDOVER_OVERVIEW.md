# Client handover overview

## What the website is

MRN Ilam is a bilingual public-service website for foreign-employment awareness, counseling, verified information, organizational transparency, membership management, and activities. It is not a manpower company, recruitment agency, visa processor, or job-guarantee service.

## What visitors can do

- Read the organization’s purpose, objective, commitment, disclaimer and chairperson message.
- Request private counseling and choose a preferred language/contact method.
- Find safe-migration guidance, fraud warnings, FAQs and verified official resources.
- Read current news, notices, safety alerts and real programs/activities.
- Search public members by name or membership number and filter by category, unit and status.
- Read membership rules and apply for General or Life Membership when verified payment settings are enabled.
- Upload payment proof through a private, signed workflow and revisit the private status page.
- Send a general contact message.
- Use the entire public interface through `/en/` or `/ne/`.

## What each admin area is for

### Core

- **Organization Information**: official identity, registration, contact, office, hours, objective, commitment, disclaimer and chairperson content.
- **Membership Payment Settings**: approved fees, recipient, official QR and bilingual payment instructions. Keep disabled until every value is verified.
- **Service Cards**: homepage descriptions of the organization’s real services.
- **Official Resources / Resource Categories**: reviewed government or official support links.
- **Emergency Resources**: verified urgent contact channels only.
- **FAQs**: public questions and answers in both languages.
- **Team Members**: leadership/committee information in both languages.
- **Contact Messages**: private general inquiries.
- **Membership Applications**: applicant information before payment approval.

### Counseling

- **Counseling Requests**: private cases, status, assignment, consent and retention state.
- **Counseling Notes**: internal case notes.
- **Contact Attempts**: when/how staff tried to reach the person and the outcome.
- **Counseling Categories**: public reasons for requesting guidance.

### Members

- **People**: one record for each individual; private contact data stays here.
- **Membership Records**: each separate General/Life/unit membership and permanent number.
- **Membership Categories**: General, Life and future approved categories.
- **Organization Units**: district, municipality and committee registries.
- **Potential Duplicates**: review similar people without deleting legitimate multiple memberships.
- **Import Batches / Import Rows**: auditable history of spreadsheet imports.
- **Number Sequences / Number Issues**: system-controlled permanent number allocation and non-reuse ledger.

### Payments

- **Manual Payments**: protected proof, transaction reference, amount and review workflow.
- **Payment Review Events**: immutable audit trail of status changes.

### Blog

- **Articles**: News, Notice, Safety Alert, Event/Program and Counseling Update. Draft and expired content is not public.

## Membership-payment workflow

1. An administrator verifies fees, recipient and official QR, then enables payment settings.
2. The applicant submits membership details.
3. The site shows the correct fee/instructions through a signed private link.
4. The applicant uploads JPG/PNG/WebP proof and an optional transaction reference.
5. The payment is Pending.
6. A Payment Reviewer checks the protected evidence.
7. Approval transactionally links/creates the person, creates the correct membership and allocates a permanent number.
8. Repeated approval does not create another membership.
9. Rejection requires a clear applicant-facing reason; internal notes remain separate.
10. Every review transition is recorded.

## Staff roles

- **Content Editor**: organization content, resources, FAQs, team and articles.
- **Membership Manager**: people, memberships, units/categories, duplicate review and imports.
- **Counseling Staff**: private counseling cases, notes and contact attempts.
- **Payment Reviewer**: protected payment evidence and approval/rejection.
- **Administrator**: full access; reserve for trusted leadership/technical staff.

Create a separate account for each staff member. Never share the superuser account.

## Routine client operations

- Publish and expire notices through Blog.
- Review new counseling/contact submissions.
- Review payment evidence and approve/reject applications.
- Archive memberships instead of deleting them.
- Export a registry backup periodically.
- Run the launch-readiness audit after major content/configuration changes.
- Confirm official resources and emergency numbers periodically.

## What requires technical access

- Deployments and environment variables.
- Database backup/restore.
- Spreadsheet import commands.
- Translation catalogue compilation after changing interface strings.
- Cloudinary/Resend/Render/Neon credentials.
- CSS/layout changes.
