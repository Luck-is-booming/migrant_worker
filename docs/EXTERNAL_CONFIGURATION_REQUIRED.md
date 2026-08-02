# External configuration still required

The code deliberately does not invent organizational facts or payment details. Obtain and verify these before launch:

## Organization facts

- Official English and Nepali names
- Registration number and registering authority
- Establishment date
- Office address and service area
- Public office hours
- Official phone and email
- Chairperson name, designation, message and approved photo
- Current committee/leadership spellings in both languages

## Membership and payment

- Approved General Membership fee
- Approved Life Membership fee
- Official payment recipient name
- Official organization-controlled QR
- Bilingual payment/account instructions
- Authorized payment reviewers and approval policy

## Connected services

- Neon PostgreSQL production URL and named backup owner
- Cloudinary credentials that permit public content uploads and authenticated private counseling/payment assets
- Resend verified sender/domain and organization notification address
- Render custom domains, allowed hosts and trusted CSRF origins
- A strong Django secret key and protected administrator credentials

## Human verification

- Review every public Nepali paragraph for natural language
- Review transliterated English member/committee names
- Verify which member fields may be public
- Verify official/emergency resource URLs and contact numbers
- Test on representative phones/tablets/laptops
- Complete one controlled payment approval and one rejection
- Complete one counseling submission and verify staff-only attachment access
