# Architecture and data boundaries

## Apps

- `core`: organization information, services, resources, FAQ, leadership, contact, membership applications, payment configuration, privacy/disclaimer/program pages.
- `counseling`: private requests, categories, notes, contact attempts, assignment, status and retention workflow.
- `members`: people, official memberships, organization units, categories, permanent number ledger, imports, duplicate review and public directory.
- `payments`: private payment evidence, status tracking, review audit and approval service.
- `blog`: bilingual news, notices, alerts, events/programs, counseling updates and localized SEO metadata.

## Person versus membership

`Person` stores one individual and private contact information. `MembershipRecord` stores each separate membership relationship. One person can therefore hold General and Life Membership, or memberships in different organizational units, without duplicating their core identity.

## Public/private boundary

Public member pages expose only approved public fields. Phone, email, payment screenshots, counseling details, source-IP hashes, internal notes, and duplicate-review evidence remain staff-only. New payment/counseling files use authenticated Cloudinary assets and five-minute signed URLs generated only after permission checks; local development/tests use default local storage.

## Business workflows

- Complex member allocation and payment approval use database transactions.
- Membership numbers are allocated by `members.numbering`, not by counting rows.
- Public payment depends on one admin-managed verified settings record.
- Imports never delete records merely because a row is absent from a later file.
- External email failure never rolls back a successfully saved form submission.
