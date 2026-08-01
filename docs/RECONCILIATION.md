# Membership source reconciliation

This report is based on direct inspection of the two supplied authoritative membership workbooks. It is **not** a claim that a production import has already run against Neon/PostgreSQL.

| Metric | Source-audit result | Production result |
|---|---:|---:|
| Total workbook rows | 278 | Run dry-run/import to confirm |
| Header/title rows | 6 | 6 expected |
| Blank rows | 3 | 3 expected |
| Non-data/summary rows | 1 | 1 expected |
| Valid data rows | 268 | 268 expected |
| Imported people | 266 expected in an empty normalized registry | Pending production dry run |
| Imported memberships | 268 expected in an empty normalized registry | Pending production dry run |
| Updated people | Depends on existing database | Pending production dry run |
| Updated memberships | Depends on existing database | Pending production dry run |
| Unchanged records | Depends on existing database | Pending production dry run |
| Multiple-membership people | 2 strong source candidates | Pending staff review |
| Potential duplicates | 2 contradictory-phone groups | Pending staff review |
| Warning rows | At least 114 blank-phone rows will require cautious handling | Pending dry-run report |
| Failed rows | 0 structural failures in source audit | Must be zero before real import |
| Database people before/after | Production access required | Pending |
| Database memberships before/after | Production access required | Pending |
| Records deleted | 0 by design | Must remain 0 |

## Strong multiple-membership candidates in the supplied data

1. **नविन सुन्दर सेर्मा / नविन सुनदर सेर्मा रकम** — same verified phone; District Life membership no. 4 and Ilam Municipality Life membership no. 1. The actual workbook does not show one General and one Life membership for Nabin; it shows two Life memberships in different units.
2. **ज्योती खड्का / ज्योति खड्का** — same verified phone; District Life membership no. 15 and Ilam Municipality General membership no. 194.

The automated tests separately cover the required General-plus-Life scenario for one person.

## Manual duplicate review

Two shared-phone groups have conflicting names and must remain separate until staff verify identity:

- पवित्रा देवी विश्वकर्मा ↔ सीता कुमारी राइ
- सोम वहादुर गुरुङ् ↔ बुदीविर गुरुङ्

The exact rows are in `audit_reports/potential-duplicate-review.csv`. No same-name-only merge is allowed.
