# MRN Ilam Admin: simple staff guide

The admin is designed around daily tasks instead of database tables.

## What a normal staff member sees

After signing in, the dashboard shows only the sections that match the staff member's role:

- Counseling requests
- General enquiries
- Membership applications
- Payment reviews
- People
- Issued memberships
- Website content
- Organization settings they are allowed to edit

Legacy member rows, old resource records, number sequences, import internals, and other technical records are not shown in the normal workspace. They remain safely in the database where required for history and compatibility.

## A simple point of view: the person who runs the website

> I log in and immediately see what needs attention. I do not need to understand Django models or database terms.
>
> If a worker asks for help, I open **Counseling requests**, read the concern, assign it to myself or another staff member, record contact attempts, add a private note, and update the status.
>
> If someone applies for membership, I open **Membership applications**. The same page links me to the payment review and, after approval, to the person record and issued membership. I do not search through several unrelated sections.
>
> If I need to post a notice, I open **News, notices and programs**, enter the verified English and Nepali versions, keep it as a draft while checking, and publish it when ready.
>
> If the chairperson changes their message or photo, I open **Organization information**, edit the message and upload the photo. The saved photo preview confirms what is currently stored, and the photo appears beside the message on the public About page.
>
> I only use **Duplicate reviews** after comparing the original records. I never manually change an issued membership number.

## Daily routine

1. Check new counseling requests, enquiries, applications, and payments.
2. Open one record and read the full details.
3. Assign or update its status.
4. Record the action or internal note.
5. Publish only verified content in both languages.
6. Leave audit and numbering records unchanged unless an administrator is investigating a problem.

## Counseling requests

Use these statuses consistently:

- **New**: not yet reviewed
- **Reviewed**: a staff member has read it
- **Contact attempted**: staff tried to contact the person
- **In counseling**: active support is being provided
- **Referred**: the person was directed to the appropriate office or professional
- **Resolved**: the main concern has been addressed
- **Closed**: no more action is expected
- **Spam**: clearly irrelevant or abusive submission

Use **Assign selected requests to me** when taking responsibility for several new requests.

## Membership applications and payments

The intended flow is:

1. Open the membership application.
2. Follow the **Open payment review** link.
3. Compare the amount, transaction reference, recipient, and screenshot.
4. Approve, request more review, or reject with a clear applicant-facing reason.
5. After approval, use the links to open the created person and issued membership.
6. Confirm the membership number once; do not edit it later.

## People and issued memberships

A **Person** is the individual. An **Issued membership** is one membership held by that person.

One person may have both General and Life Membership. This is valid and must not be merged or deleted simply because the names match.

Private phone and email details stay inside Admin. The public directory shows only approved non-sensitive fields.

## Publishing website content

For news, notices, programs, resources, FAQs, team members, and homepage services:

- use verified facts;
- complete both English and Nepali fields;
- use clear titles;
- add useful image descriptions;
- save as draft while checking;
- publish only when ready;
- archive outdated content instead of deleting it.

## Chairperson photo

The Organization Information page now shows a preview of the saved chairperson photo. The public About page displays that same photo beside the message.

For best results:

- use a clear portrait;
- avoid screenshots with large blank borders;
- keep the person's face near the upper center;
- use an image you have permission to publish.

## Technical and legacy records

The following are hidden from normal staff:

- legacy flat member records;
- legacy resource publications;
- membership number sequences;
- membership number audit history;
- member import history;
- unused destination-country records.

Superusers may access some audit records when investigating a problem. These records should not be edited or deleted.

## Safety rules

- Never delete people to fix a spelling mistake.
- Never reuse or manually renumber a membership number.
- Never merge two people based only on a similar name.
- Never expose payment screenshots or counseling attachments publicly.
- Never put sensitive personal details in public content.
- Never publish unverified organization details, emergency contacts, or payment information.
