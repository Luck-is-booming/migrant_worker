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
