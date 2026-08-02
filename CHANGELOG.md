# Changelog

## Client-ready final rebuild — 2026-08-02

### Membership integrity
- Added normalized people and multiple memberships per person.
- Added database-scoped membership number sequences and permanent issuance ledger.
- Added non-reuse after archive/deletion, immutable issued numbers, archive/restore actions that preserve prior public visibility, and scoped uniqueness constraints.
- Defaulted authoritative imported roster rows to Active instead of Unknown when no contrary source value exists.
- Preserved numeric ordering in public search and exports.
- Added privacy-safe CSV/JSON export and repeatable Excel imports.

### Membership application and payment
- Replaced the bundled personal/static QR with an administrator-managed verified payment configuration.
- Public application remains paused until official fees, recipient, and QR are verified.
- Added proof validation, randomized private paths, duplicate transaction-reference prevention, signed private status links, protected staff evidence access, rejection reasons, audit events, and idempotent approval.
- Approval now creates or links one person, creates one official membership, and allocates a permanent number transactionally.

### Public experience
- Added membership information, programs, privacy, disclaimer, complete error pages, stable root redirect, bilingual navigation, query-preserving language switch, responsive navy design, strict language-specific member/resource fields, localized article SEO metadata, and long-content resilience.
- Added article image descriptions and automatic notice expiry.
- Added verified official-resource/FAQ seed command without invented organizational claims.

### Admin and security
- Added least-privilege staff roles, read-only audit fields, archive/restore actions, duplicate review, payment readiness checks, authenticated Cloudinary storage for new counseling/payment files, short-lived signed staff access, legacy-private-file audit, admin login throttling, secure headers, and production-safe defaults.
- Added bilingual leadership fields and an idempotent district executive committee import command.

### Quality and deployment
- Added critical workflow tests, PDF signature validation, PostgreSQL-only concurrency verification, launch-readiness audit, clean Render build, environment documentation, deployment/rollback guide, and client administration guide.

## 2026-08-02 runtime verification hotfix

- Fixed singleton payment settings so a second create updates the one existing row instead of failing unique validation.
- Added the missing migration aligning consent timestamps with `auto_now_add=True`.
- Removed five duplicate favicon sources that caused `collectstatic` conflicts.

## Final plain-language and responsive refinement — 2026-08-02

### Reader experience
- Rewrote the public interface in clear, practical language and removed reader-facing policy, database, and workflow jargon.
- Simplified the homepage, counseling process, guidance, safety, membership, payment, member search, privacy, disclaimer, resources, news, programs, and error states.
- Kept verified organization facts, names, leadership, slogan, objective, commitment, addresses, and registration details under Django Admin control.
- Added a guarded data migration that refreshes only the known legacy service-card copy; custom administrator-written services are not overwritten.

### English and Nepali
- Added natural Nepali translations for the final public copy, form labels, help text, validation guidance, empty states, payment instructions, and error pages.
- Removed the obsolete duplicate transaction-reference translation and regenerated the compiled catalogue.
- Validated the catalogue with no duplicate, empty, or fuzzy active messages.

### Navigation, accessibility, and responsive layout
- Rebuilt the header into a spacious desktop navigation and an accessible mobile drawer before links become cramped.
- Added reliable close behavior for link selection, outside click, Escape, and viewport changes, with body-scroll locking and focus handling.
- Added 44-pixel touch targets, visible focus styles, skip navigation, clear form relationships, accessible status/error regions, reduced-motion support, mobile-safe member/payment layouts, and 200%-zoom resilience.

### Official logo consistency
- Kept the existing organization seal unchanged and made it the single source for navigation, footer, favicon, Apple touch icon, web-app manifest, Open Graph image, and maintenance branding.
- Removed conflicting duplicate/static logo sources and generated proportion-preserving favicon sizes from the approved seal.

### Production reliability
- Included the PostgreSQL non-atomic membership-number migration fix required by the live Neon database.
- Preserved routes, security controls, private uploads, payment approval, membership numbering, existing member data, and deployment configuration.

## Final administration and chairperson display refinement — 2026-08-02

### Staff workspace
- Added a task-focused MRN Ilam dashboard with counts for new counseling requests, enquiries, open applications, payment reviews, public people, active memberships, duplicate reviews, and unpublished content.
- Reorganized the admin around daily work, website content, organization settings, and protected review/audit tools.
- Replaced technical labels with plain staff-facing names such as Payment Reviews, Issued Memberships, General Enquiries, Membership Units, and Duplicate Reviews.
- Added direct links between membership applications, payments, people, and issued memberships.
- Added clear status badges, simpler field groups, safer quick actions, and role-aware navigation.

### Legacy and audit protection
- Removed the legacy flat Member and legacy Resource Publication models from Django Admin without deleting their tables or data.
- Restricted numbering sequences, number audit history, import history, and unused destination-country records to superusers.
- Kept number and import audit screens read-only.
- Removed legacy SEO fields from the normal article editing form while retaining the underlying data.

### Chairperson and branding
- Added a current-photo preview to Organization Information in Admin.
- Displayed the saved chairperson photo beside the message on the public About page with a responsive layout.
- Used the existing approved MRN Ilam logo and favicon in Admin without changing the brand asset.

### Quality
- Fixed the shared form partial by loading Django i18n tags directly, resolving the three reported template test errors.
- Added a non-technical staff guide at `docs/ADMIN_OPERATIONS_GUIDE.md`.
- Added no schema migration and changed no production data, member records, membership numbers, payment records, or verified organization content.
