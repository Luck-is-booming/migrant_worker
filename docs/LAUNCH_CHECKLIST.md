# Final launch checklist

## Verified facts
- [ ] Official English and Nepali organization names
- [ ] Registration number and authority
- [ ] Establishment date
- [ ] Office address, service area and hours
- [ ] Official phone and email
- [ ] Chairperson name/message approved in both languages

## Payment
- [ ] Approved General and Life fees entered in admin
- [ ] Official QR uploaded
- [ ] Recipient confirmed by scanning on two devices
- [ ] Bilingual payment instructions entered
- [ ] One test application submitted
- [ ] Proof opened through protected admin URL
- [ ] Approval created exactly one membership/number
- [ ] Rejection and private status link tested

## Content
- [ ] Official resources reviewed and dated
- [ ] Emergency channels verified by authorized staff
- [ ] At least one current bilingual notice/article published
- [ ] Programs page contains only real activities
- [ ] No placeholder organizational fact remains

## Privacy/security
- [ ] Separate staff accounts and least-privilege groups
- [ ] No private phone/email visible in member pages
- [ ] Counseling and payment files require authorized admin access
- [ ] Resend sender verified before email enabled
- [ ] Public Cloudinary image upload tested
- [ ] Authenticated counseling/payment upload and staff-only retrieval tested
- [ ] Legacy private-media audit reviewed and old public evidence migrated/re-uploaded where required
- [ ] `DEBUG=False`, strong `SECRET_KEY`, correct hosts/origins
- [ ] HSTS enabled only after HTTPS/subdomain review

## Quality
- [ ] All tests pass
- [ ] `makemigrations --check --dry-run` says no changes
- [ ] English and Nepali pages manually reviewed
- [ ] 320px phone, modern phone, tablet, 1366×768 laptop and desktop checked
- [ ] Keyboard navigation and focus states checked
- [ ] Sitemap succeeds and `/en/`, `/ne/` are crawlable
- [ ] Database backup and rollback owner confirmed
