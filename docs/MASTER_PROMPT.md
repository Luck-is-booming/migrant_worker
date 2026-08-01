# MASTER PROMPT — COMPLETE REBUILD OF MRNILAM.ORG.NP

Act as a senior product designer, UX researcher, Django architect, frontend engineer, database engineer, accessibility specialist, security engineer, SEO specialist, content strategist, and deployment engineer.

Rebuild **mrnilam.org.np** completely from the ground up.

Do not treat this as a small redesign, theme update, or surface-level refactor. Reconsider the entire information architecture, user journey, visual system, database structure, multilingual experience, administration workflow, performance, accessibility, security, and deployment process.

The finished website should feel like a trustworthy, established, community-focused public-service organization—not a generic template, visa consultancy, recruitment agency, or AI-generated landing page.

Prioritize quality, reliability, clarity, maintainability, and real-world usability over speed.

---

# 1. ORGANIZATION PURPOSE

The website represents an organization in Ilam that supports people seeking information and guidance related to foreign employment and migration.

The organization primarily provides:

* Counseling and guidance
* Awareness about safe foreign employment
* Information about migration risks
* Education about fraud and exploitation
* Guidance about documentation and preparation
* Referral to appropriate services or authorities
* Community outreach
* Membership and organizational information
* News, notices, resources, and awareness content

The organization is **not**:

* A visa agency
* A manpower company
* A recruitment agency
* A travel agency
* A company promising overseas jobs
* A service that guarantees visas, jobs, or migration outcomes

This distinction must be clearly reflected throughout the website.

Avoid language such as:

* “We will send you abroad”
* “Guaranteed visa”
* “Guaranteed job placement”
* “Apply through us”
* “Get your visa approved”

Use responsible language such as:

* “Receive counseling and reliable information”
* “Understand safe migration procedures”
* “Learn how to identify fraud”
* “Prepare before making migration-related decisions”
* “Connect with appropriate support services”

Add a clear, respectful disclaimer stating that the organization provides information and counseling but does not guarantee visas, employment, recruitment, or migration outcomes.

---

# 2. CORE PRODUCT GOAL

Build the most trustworthy, intuitive, accessible, and professional digital presence possible for the organization.

The website should help a visitor immediately understand:

1. Who the organization is
2. What assistance it provides
3. What it does not provide
4. How to request counseling
5. How to contact the organization
6. How to verify organizational members
7. How to access notices, resources, and awareness information
8. How to become a member or complete a membership-related payment
9. How to use the entire website in either English or Nepali

A visitor should never feel confused about where to click or what action to take next.

---

# 3. NON-NEGOTIABLE REQUIREMENTS

## 3.1 Preserve all existing member data

There is an existing Excel file containing member information.

Every legitimate member in that Excel file must be preserved.

Do not:

* Delete members silently
* Merge different people without evidence
* Lose membership numbers
* Replace missing information with invented data
* Remove a person because they appear more than once
* Assume that multiple membership records are duplicates

A single person may belong to more than one membership category.

For example, a person such as **Nabin** may be both:

* A General Member
* A Life Member

These must remain separate membership records connected to the same person where appropriate.

Design the data model so that:

* One person can have multiple memberships
* Each membership has its own type, level, unit, number, status, and relevant dates
* Duplicate people can be identified without destroying valid multiple memberships
* Importing the Excel file is repeatable and safe
* Re-running an import does not create uncontrolled duplicates
* Existing data is backed up before imports or destructive operations

Create:

* A robust Excel import command
* Validation reports
* Duplicate warnings
* Import previews or dry-run support
* Clear error reporting
* A JSON or CSV backup/export command
* Automated tests for the import process

No member should disappear because of a refactor, migration, re-import, or deployment.

## 3.2 Membership numbering

Maintain unique membership numbers according to the organization’s real structure.

Membership numbers should be unique within the appropriate combination of:

* Organizational level
* Unit or committee
* Membership type

Store the numeric component separately where useful so members can be sorted numerically rather than alphabetically.

For example, sorting should place:

* 2 before 10
* 10 before 100

Do not sort numeric membership values as plain strings.

## 3.3 Completely bilingual

Everything publicly visible in English must also be available in Nepali.

Do not create a hybrid-language interface.

Unacceptable examples:

* An English heading with a Nepali button
* An English paragraph containing random Nepali labels
* Navigation where some links are translated and others are not
* Nepali pages that still display English validation errors
* English pages displaying untranslated model names or messages

The English version must be fully English.

The Nepali version must be fully Nepali.

This applies to:

* Navigation
* Buttons
* Forms
* Placeholders
* Validation messages
* Success messages
* Error messages
* Empty states
* Search controls
* Filters
* Member categories
* Membership statuses
* Notices
* Footer content
* Accessibility labels
* Confirmation dialogs
* Pagination
* Payment instructions
* Contact information labels
* Counseling request forms
* Privacy notices
* System-generated public messages
* 404 and 500 pages

Use Django’s proper internationalization framework.

Do not maintain two unrelated hardcoded websites.

Use translation files, localized content models where appropriate, and reusable translated interface components.

Recommended URL structure:

* `/en/`
* `/ne/`

The language switcher must:

* Be visible but unobtrusive
* Clearly show “English” and “नेपाली”
* Preserve the visitor’s current page wherever possible
* Preserve safe query parameters such as search and filters
* Remember the selected language
* Never unexpectedly mix both languages
* Fall back safely when a translation is unavailable

Add correct:

* `lang` attributes
* `hreflang` tags
* Localized metadata
* Localized page titles
* Localized descriptions
* Localized Open Graph metadata
* Localized sitemap entries

Use natural, respectful Nepali. Do not use awkward word-for-word machine translation.

---

# 4. VISUAL DIRECTION

## 4.1 Theme

Use a sophisticated **navy-blue visual identity**.

Suggested foundation:

* Primary deep navy: `#0B1F3A`
* Dark navy: `#071426`
* Medium navy: `#173B64`
* Soft blue-gray: `#EAF0F6`
* Off-white background: `#F8FAFC`
* White surfaces: `#FFFFFF`
* Main text: `#172033`
* Muted text: `#5D6878`
* Success: restrained accessible green
* Warning: restrained accessible amber
* Error: accessible deep red

These values may be refined, but the website must remain visibly navy-led.

Do not make the entire website dark blue.

Use navy strategically for:

* Header
* Footer
* Primary buttons
* Important section backgrounds
* Strong headings
* Trust indicators
* Active states

Balance it with white space, light neutral surfaces, readable text, and restrained accent colors.

## 4.2 Desired personality

The website should feel:

* Trustworthy
* Calm
* Human
* Responsible
* Community-centered
* Professional
* Respectful
* Transparent
* Modern without being trendy
* Visually polished without being flashy
* Appropriate for government, nonprofit, and community audiences

Avoid:

* Neon colors
* Excessive gradients
* Glassmorphism everywhere
* Large decorative blobs
* Unnecessary floating shapes
* Overdone animations
* Fake statistics
* Generic corporate stock-template styling
* Visa and airplane imagery on every section
* Passport stamps used as decoration
* “Get started” buttons with no clear meaning
* AI-style layouts with repetitive cards
* Oversized headings that consume the entire screen
* Decorative elements that reduce trust
* Auto-playing videos
* Aggressive popups
* Fake testimonials
* Claims that cannot be verified

## 4.3 Typography

Use highly readable typography that supports both English and Nepali correctly.

Choose font families with:

* Excellent Devanagari rendering
* Clear English characters
* Good readability on inexpensive Android devices
* Consistent visual weight across languages
* Proper numeral rendering

Load fonts efficiently and include strong system-font fallbacks.

Do not allow missing glyphs, broken conjuncts, incorrect line heights, or Nepali text clipping.

Use a clear typographic hierarchy:

* Page title
* Section title
* Subsection title
* Body text
* Supporting text
* Form labels
* Captions
* Metadata

Keep paragraph widths comfortable and avoid dense walls of text.

---

# 5. RESPONSIVE DESIGN

The website must work correctly and look intentional on:

* Small Android phones
* Older low-resolution phones
* iPhone SE-sized screens
* iPhone 16 and similar devices
* Large modern phones
* Tablets in portrait and landscape
* 11-inch to 14-inch laptops
* Common 1366×768 Acer and Dell laptops
* Full HD monitors
* Wide desktop screens

Test important breakpoints rather than merely adding generic media queries.

There must be:

* No horizontal scrolling
* No clipped Nepali text
* No overlapping navigation
* No overflowing member tables
* No buttons extending outside the viewport
* No unusably small tap targets
* No fixed elements covering content
* No modal taller than the screen without scrolling
* No form fields hidden by mobile keyboards
* No layout shift caused by images
* No desktop-only hover dependency
* No broken language switcher on mobile
* No awkward empty spaces at medium widths

Minimum touch targets should generally be around 44×44 CSS pixels.

Member data should not be forced into an unreadable table on mobile. Use responsive cards, collapsible details, or a thoughtfully designed mobile representation.

---

# 6. INTERNATIONAL AND CROSS-COUNTRY ACCESS

The website must open reliably for users in Nepal, India, the Gulf region, Malaysia, Europe, the United States, and other countries.

Do not build country-specific assumptions into the technical architecture.

Ensure:

* No geographic blocking
* No India-only or Nepal-only CDN dependency
* HTTPS everywhere
* Secure redirects
* Correct Unicode handling
* UTF-8 throughout the application and database
* International DNS reliability
* Globally accessible static and media delivery
* Reasonable performance on high-latency connections
* Low-bandwidth usability
* Graceful behavior when JavaScript loads slowly or fails
* No critical content dependent on third-party scripts
* No hardcoded server timezone assumptions
* Correct timezone-aware timestamps
* Correct date formatting for each language
* International phone-number input support
* Nepal as a sensible default where appropriate, but not as a restriction
* Country codes stored separately or in normalized international format
* Server-side validation for phone numbers
* Email addresses and international characters handled correctly

Do not rely on the visitor being located in Nepal.

Do not redirect users based solely on IP location.

Language choice should be under the visitor’s control.

---

# 7. INFORMATION ARCHITECTURE

Create a simple, clear navigation structure.

Recommended primary navigation:

* Home
* About
* Services / Counseling
* Safe Migration Resources
* Members
* News and Notices
* Contact

Possible secondary pages:

* About the Organization
* Mission and Objectives
* Leadership or Committees
* Organizational Structure
* Counseling Guidance
* Fraud Awareness
* Before Going Abroad
* While Working Abroad
* Returning Home
* Emergency and Support Contacts
* Membership Information
* Membership Payment
* Privacy Policy
* Terms or Disclaimer
* Frequently Asked Questions

Do not expose unnecessary pages merely because a database model exists.

Navigation labels should describe the destination clearly.

Avoid vague labels such as:

* Explore
* Discover
* Learn More

Use them only when their destination is obvious from context.

---

# 8. HOMEPAGE

Design the homepage as a guided introduction, not a collection of unrelated sections.

Recommended flow:

## 8.1 Trustworthy hero

Include:

* Clear statement of who the organization serves
* Clear explanation of its counseling and awareness role
* One strong primary action
* One useful secondary action
* A relevant, authentic image or restrained visual treatment
* No misleading promise of employment or visas

Possible primary action:

* Request Counseling

Possible secondary action:

* Learn About Safe Migration

## 8.2 Immediate help options

Provide a concise section helping visitors choose what they need:

* I need counseling
* I want to verify information
* I want safe migration guidance
* I want to contact the organization
* I am looking for member information
* I want to read notices

## 8.3 What the organization does

Explain its role using plain language.

Do not overwhelm users with institutional terminology.

## 8.4 Safe migration guidance

Highlight the most important awareness resources.

## 8.5 Latest notices

Display only current, published notices.

Include clear dates and localized formatting.

## 8.6 Organization trust section

Use verifiable trust indicators such as:

* Official contact details
* Physical location
* Registered organizational information where available
* Transparent leadership or committee details
* Privacy commitment
* Clear service disclaimer

Do not invent statistics, awards, registrations, partnerships, or impact figures.

## 8.7 Contact and counseling call to action

Finish with a direct, calm invitation to request support.

---

# 9. COUNSELING REQUEST SYSTEM

Create a professional counseling or inquiry form.

Required fields should include:

* Full name
* Phone number
* Subject or reason for contacting
* Message or description
* Preferred language
* Consent to the privacy notice

Optional fields may include:

* Email address
* District or location
* Preferred contact method
* Best time to contact
* Relevant category

The phone number must be required.

The form must:

* Work without confusing technical errors
* Preserve safe input after validation failure
* Use server-side validation
* Include spam protection
* Include rate limiting
* Never expose private submissions publicly
* Store timestamps safely
* Show a clear success state
* Send a notification email to the organization
* Optionally send a confirmation email to the visitor
* Avoid claiming that a response is guaranteed within an invented timeframe

The admin interface should support:

* New
* In review
* Contacted
* Resolved
* Spam or invalid

Protect personal information carefully.

Do not include sensitive submission details in analytics tools, URLs, or logs.

---

# 10. MEMBERS DIRECTORY

Create a professional, searchable member directory.

Users should be able to search and filter by appropriate fields such as:

* Name
* Membership number
* Membership type
* Organizational level
* Unit or committee
* Municipality or relevant location
* Status, where publicly appropriate

Requirements:

* Fast search
* Clear empty states
* Pagination
* Accessible filter controls
* Mobile-friendly presentation
* Numeric membership-number ordering
* Bilingual labels
* Clear distinction between General and Life membership
* Ability for one person to appear under multiple valid membership records
* No leaking of private information

Do not publicly expose sensitive data such as:

* Private phone numbers
* Home addresses
* Identity documents
* Payment screenshots
* Internal notes
* Personal email addresses unless explicitly approved for publication

Provide a useful member detail view only when it adds value.

Publicly visible fields should be explicitly controlled through model or admin settings.

---

# 11. MEMBERSHIP APPLICATION AND PAYMENT

Where membership application or payment is supported, retain the existing manual payment model unless a verified online gateway is deliberately added.

The manual payment flow may include:

1. User selects the relevant membership category
2. User reviews the fee and instructions
3. User sees the official QR code or payment account details
4. User completes payment externally
5. User submits:

   * Full name
   * Phone number
   * Membership category
   * Payment reference where available
   * Payment screenshot
   * Other genuinely required information
6. Submission enters a pending state
7. An administrator reviews it
8. Administrator approves or rejects it
9. On approval, the correct membership record is created or linked
10. The action is logged

Requirements:

* Never create duplicate members automatically without checking
* Do not create a member before approval
* Keep payment evidence private
* Validate uploaded files
* Restrict file type and size
* Prevent executable uploads
* Use secure media URLs where possible
* Record who approved or rejected a request
* Prevent multiple approvals from creating multiple memberships
* Use database transactions
* Make the approval process idempotent
* Allow administrators to add notes
* Clearly communicate pending, approved, and rejected states
* Translate every public status message

Do not imply that online payment alone guarantees membership acceptance.

---

# 12. NEWS, NOTICES, AND RESOURCES

Create a simple publishing system for:

* News
* Notices
* Awareness articles
* Safe-migration resources
* Emergency information
* Downloadable documents

Content entries should support:

* English title
* Nepali title
* English summary
* Nepali summary
* English body
* Nepali body
* Featured image
* Accessible alt text in both languages
* Publication status
* Publication date
* Optional expiry date for notices
* Slug
* SEO title and description
* Category
* Author or publishing office
* Attachments where needed

Do not show draft content publicly.

Expired notices should be archived rather than deleted.

Provide clear distinctions between:

* News
* Time-sensitive notices
* Permanent educational resources

Avoid presenting old notices as current.

---

# 13. CONTENT QUALITY

Rewrite the public-facing content so it is:

* Clear
* Calm
* Credible
* Respectful
* Factually responsible
* Easy to understand
* Free from unnecessary jargon
* Useful to first-time visitors
* Appropriate for people with different education levels

Do not fill pages with placeholder text.

Do not fabricate:

* Addresses
* Phone numbers
* Registration numbers
* Committee names
* Partnerships
* Testimonials
* Statistics
* Impact claims
* Government recognition
* Awards

Where verified information is missing, use a clearly marked content placeholder for the administrator rather than inventing facts.

Nepali content must be natural and professionally written—not a mechanical translation of English sentence structure.

---

# 14. TRUST AND TRANSPARENCY

Trustworthiness must come from real design and information, not decorative badges.

Include:

* Clear organization identity
* Consistent official contact information
* Physical location or service area where verified
* Transparent explanation of services
* Clear disclaimer
* Privacy policy
* Secure forms
* Visible last-updated dates where useful
* Publication dates on articles and notices
* Real committee or organizational information where supplied
* Clear distinction between official information and general guidance
* Links to relevant official authorities where appropriate
* A way to report inaccurate information

Do not add fake “verified,” “certified,” or “government approved” badges.

---

# 15. ACCESSIBILITY

Target WCAG 2.2 AA-level usability.

Include:

* Semantic HTML
* Logical heading order
* Keyboard-accessible navigation
* Visible focus states
* Skip-to-content link
* Accessible forms and labels
* Error summaries
* Screen-reader-friendly validation
* Sufficient color contrast
* Meaningful link text
* Appropriate button elements
* Accessible dialogs
* Correct table semantics where tables are necessary
* Alt text management
* Reduced-motion support
* No information communicated by color alone
* Correct language declaration for English and Nepali sections

Animations must respect `prefers-reduced-motion`.

Do not use animation on every scroll event.

---

# 16. PERFORMANCE

The site should perform well on low-cost mobile devices and slower connections.

Optimize:

* Images
* Fonts
* CSS
* JavaScript
* Database queries
* Pagination
* Static files
* Caching
* Compression
* Server response time

Use:

* Responsive images
* Modern image formats where supported
* Explicit width and height attributes
* Lazy loading for below-the-fold media
* Database indexes for common searches
* `select_related` and `prefetch_related`
* Query-count testing for important pages
* Efficient pagination
* Minimized blocking scripts
* Local or privacy-respecting critical assets where practical

Avoid shipping a large JavaScript framework unless it provides a genuine benefit.

Core navigation, content, search submissions, and forms should remain usable without fragile client-side behavior.

Target strong Core Web Vitals without compromising functionality.

---

# 17. SEARCH ENGINE OPTIMIZATION

Implement technical SEO properly.

Include:

* Localized titles and descriptions
* Canonical URLs
* `hreflang`
* XML sitemap
* Localized sitemap entries
* Robots configuration
* Structured breadcrumbs
* Organization structured data using verified details only
* Article structured data where appropriate
* Correct Open Graph metadata
* Social preview images
* Descriptive URLs
* Permanent redirects for replaced URLs
* Proper 404 handling
* Prevention of accidental indexing of admin, drafts, private files, and filtered duplicates

Preserve or redirect important existing URLs so the rebuild does not unnecessarily destroy existing indexing.

Do not generate thousands of low-value filter URLs for search engines.

---

# 18. SECURITY AND PRIVACY

Apply production-level Django security.

Include:

* Environment variables for secrets
* `DEBUG=False` in production
* Secure allowed-host configuration
* CSRF protection
* Secure cookies
* HTTP-only cookies
* SameSite settings
* HTTPS redirect
* HSTS after confirming HTTPS stability
* Content Security Policy
* Referrer policy
* Permissions policy
* Clickjacking protection
* MIME-sniffing protection
* Safe file-upload validation
* Rate limiting
* Brute-force protection for admin login
* Strong password requirements
* Role-based admin permissions
* Audit logging for sensitive actions
* Database transactions for approval workflows
* Safe error pages
* No secrets committed to Git
* No personally identifiable information in application logs
* Backups and restore documentation

Admin pages should not rely solely on using a hidden URL as security.

Use real authentication, authorization, and security controls.

---

# 19. ADMIN EXPERIENCE

The Django admin should be customized for practical daily use.

Create:

* Clear list columns
* Useful filters
* Search fields
* Safe bulk actions
* Read-only audit fields
* Status indicators
* Organized fieldsets
* Inline memberships for a person where appropriate
* Preview links for published content
* Validation that prevents invalid membership combinations
* Duplicate-member warnings
* Approval workflows
* Export tools
* Content translation completeness indicators

Administrative roles may include:

* Super administrator
* Content editor
* Membership manager
* Counseling manager
* Payment reviewer

Each role should receive only the permissions it needs.

Do not allow ordinary content editors to access private counseling submissions or payment evidence unless authorized.

---

# 20. RECOMMENDED TECHNICAL STACK

Use a maintainable, production-ready stack.

Recommended foundation:

* Python
* Django 5 or a current stable supported version
* PostgreSQL
* Django templates
* Tailwind CSS built properly rather than relying permanently on a CDN
* Minimal vanilla JavaScript or lightweight progressive enhancement
* WhiteNoise or an appropriate static-file solution
* Cloudinary or another properly configured media-storage provider
* Render-compatible deployment
* Neon PostgreSQL or another reliable managed PostgreSQL service
* SMTP or a transactional email provider
* `django-environ` or equivalent environment configuration
* `pytest` or Django’s test framework
* Ruff
* Black
* Type checking where useful
* Pre-commit hooks

Do not add complex dependencies without a clear reason.

Pin production dependencies.

Document required environment variables.

---

# 21. CLOUDINARY AND MEDIA HANDLING

Configure media storage correctly.

The current system has experienced Cloudinary permission errors, including failures involving missing `create` permissions.

Do not hide these failures.

Implement:

* Correct credentials and cloud configuration
* Separate development and production handling
* Upload validation
* Meaningful error messages
* Secure transformations
* Predictable folder structure
* Public versus private media decisions
* Fallback behavior
* Tests that do not require real Cloudinary uploads
* Mock storage for automated tests
* Cleanup strategy for replaced or deleted files
* Documentation for required Cloudinary permissions

Do not make the entire admin form fail silently when a media upload fails.

---

# 22. EMAIL

Implement reliable email handling for:

* Counseling submissions
* Contact-form notifications
* Optional visitor confirmations
* Membership-payment notifications
* Approval or rejection notifications where appropriate
* Administrative error reporting where appropriate

Requirements:

* Use environment-based SMTP configuration
* Do not hardcode credentials
* Use clear plain-text and HTML versions
* Translate user-facing emails
* Avoid exposing private data unnecessarily
* Log delivery failures safely
* Do not block the entire request indefinitely when an email provider is slow
* Provide a safe retry strategy where appropriate

A successful form submission should not be lost solely because an email notification failed.

---

# 23. ERROR HANDLING

Create polished bilingual:

* 400 page
* 403 page
* 404 page
* 429 page
* 500 page
* Maintenance page

Errors should:

* Use plain language
* Explain what the visitor can do
* Provide a safe way back
* Avoid exposing stack traces
* Avoid mixed English and Nepali
* Work without JavaScript
* Match the main website design

Log server-side errors with enough context for debugging without recording sensitive information.

---

# 24. TESTING

Create meaningful automated tests.

At minimum, test:

## Data

* Excel import
* Repeat imports
* Multiple memberships for one person
* Numeric membership ordering
* Duplicate detection
* Backup and restoration
* Invalid rows
* Membership uniqueness rules

## Public pages

* English and Nepali routes
* No accidental mixed-language interface
* Homepages
* Member search
* Member filters
* Pagination
* News and notices
* Expired notices
* Contact form
* Counseling form
* Custom error pages

## Payment workflow

* Pending submission
* Approval
* Rejection
* Duplicate approval prevention
* Member creation on approval
* Existing-person matching
* File validation
* Permission checks

## Security

* Anonymous admin access denied
* Role permissions
* CSRF behavior
* Private uploads not exposed
* Draft content not public
* Counseling information protected

## Performance

* Reasonable query counts
* Pagination under larger datasets
* No N+1 query problems on important pages

Run tests in CI before deployment.

---

# 25. DEPLOYMENT

Provide a reliable deployment configuration for Render or a similarly suitable platform.

Include:

* Production settings module
* Environment variable documentation
* Build command
* Migration command
* Static file collection
* Safe release procedure
* Health-check endpoint
* Gunicorn configuration
* Correct Django WSGI module
* Database connection handling
* Allowed-host setup
* HTTPS configuration
* Media-storage configuration
* Email configuration
* Logging
* Backup procedure
* Rollback procedure

Do not use an incorrect generic command such as:

`gunicorn app:app`

Use the actual Django project WSGI application, for example:

`gunicorn project_name.wsgi:application`

Replace `project_name` with the real Django configuration package.

Never automatically seed or overwrite production data on every deployment.

Migrations must not delete existing member records unexpectedly.

Before any destructive schema or data migration:

1. Create a backup
2. Validate the backup
3. Document the migration
4. Provide a rollback path

---

# 26. PROJECT STRUCTURE

Use a clean modular architecture.

Possible Django apps:

* `core`
* `pages`
* `members`
* `counseling`
* `contact`
* `content`
* `payments`
* `accounts`
* `audit`

Do not create unnecessary apps merely for appearance.

Separate:

* Business logic
* Forms
* Services
* Selectors or query logic
* Models
* Views
* Templates
* Translation strings
* Import utilities
* Storage utilities
* Tests

Avoid oversized views and model methods containing unrelated workflows.

Use services and database transactions for complex approval operations.

---

# 27. DESIGN SYSTEM AND COMPONENTS

Create a reusable design system covering:

* Header
* Mobile navigation
* Language switcher
* Buttons
* Links
* Form fields
* Alerts
* Status badges
* Cards
* Content sections
* Breadcrumbs
* Search
* Filters
* Pagination
* Modal or dialog patterns
* Empty states
* Notice banners
* Tables
* Mobile member cards
* Footer
* Loading states
* Error states
* Success states

Every component must have:

* Default state
* Hover state where relevant
* Focus-visible state
* Disabled state
* Error state where relevant
* Mobile behavior
* Dark-background behavior where relevant
* English and Nepali compatibility

Keep border radii, shadows, spacing, typography, and icon treatment consistent.

Use icons only when they improve understanding.

Icons must never replace essential text labels.

---

# 28. ANIMATION

Use restrained motion only where it improves clarity.

Appropriate examples:

* Mobile menu opening
* Accordion expansion
* Subtle button feedback
* Smooth but brief state transitions
* Gentle reveal of non-critical content

Avoid:

* Constant floating objects
* Large parallax effects
* Repeated scroll-triggered animations
* Animation that delays access to information
* Motion-heavy hero sections
* Animated counters with unverifiable statistics
* Cursor effects
* Background particles
* Excessive page transitions

The website must remain dignified and fast.

---

# 29. ANALYTICS AND PRIVACY

Where analytics are required, use a privacy-respecting setup.

Do not:

* Send form contents to analytics
* Track uploaded filenames
* Record counseling messages
* Store full phone numbers in analytics
* Use invasive tracking without disclosure
* Load unnecessary advertising trackers

Track only useful aggregate events such as:

* Language selected
* Counseling page viewed
* Counseling form successfully submitted
* Resource opened
* Contact action selected
* Member search used

Provide a clear cookie or analytics disclosure where legally or ethically appropriate.

---

# 30. DELIVERABLES

Produce a complete working project, not disconnected snippets.

Deliver:

1. Full Django project source
2. Clean responsive frontend
3. Complete English interface
4. Complete Nepali interface
5. Translation files
6. Member data model
7. Safe Excel import command
8. Member backup/export command
9. Member search and filtering
10. Counseling request system
11. Contact system with required phone number
12. News, notices, and resources system
13. Membership-payment workflow
14. Admin approval workflow
15. Customized Django admin
16. Production settings
17. Secure media handling
18. Email configuration
19. Automated tests
20. Deployment files
21. Environment-variable example file
22. Setup instructions
23. Deployment instructions
24. Backup and restore instructions
25. Data-migration documentation
26. Content-management guide
27. Accessibility review
28. Performance review
29. Security checklist
30. Final pre-launch checklist

Do not use placeholder implementations for core functionality.

---

# 31. IMPLEMENTATION PROCESS

Follow this order:

## Phase 1: Audit and preservation

* Inspect the existing project
* Inspect the Excel file
* Map all existing member fields
* Export a verified backup
* Identify existing URLs
* Identify public content that must be preserved
* Identify private data
* Identify current deployment variables
* Document current failures

## Phase 2: Architecture

* Design the database
* Design person-versus-membership relationships
* Design translation strategy
* Design permissions
* Design payment workflow
* Design content structure
* Design URL strategy
* Create migration plan

## Phase 3: Design system

* Establish navy-blue visual identity
* Define typography
* Define spacing
* Define responsive behavior
* Create core components
* Validate Nepali font rendering

## Phase 4: Public experience

* Build navigation
* Build homepage
* Build service and counseling pages
* Build member directory
* Build resources
* Build news and notices
* Build contact experience
* Build bilingual errors

## Phase 5: Workflows

* Counseling submissions
* Contact submissions
* Membership applications
* Manual payments
* Administrative approval
* Member creation or linking
* Email notifications

## Phase 6: Data migration

* Dry-run the member import
* Review warnings
* Validate counts
* Validate multiple memberships
* Compare source and destination totals
* Import into staging
* Conduct manual sampling
* Back up before production import
* Import into production

## Phase 7: Hardening

* Security review
* Accessibility review
* Performance optimization
* Cross-browser testing
* Low-bandwidth testing
* Mobile-device testing
* International-access testing
* SEO review

## Phase 8: Launch

* Final backup
* Deploy
* Run migrations
* Verify health checks
* Verify forms
* Verify email
* Verify media
* Verify English and Nepali
* Verify member counts
* Submit sitemap
* Monitor errors

---

# 32. ACCEPTANCE CRITERIA

The rebuild is complete only when all the following are true:

* Every valid existing member is preserved
* One person can hold multiple memberships
* General and Life memberships are not wrongly merged
* Member numbers sort correctly
* English pages contain a fully English interface
* Nepali pages contain a fully Nepali interface
* No visible hybrid-language pages remain
* The contact form requires a phone number
* The organization is presented as a counseling and awareness service
* No page suggests guaranteed visas or employment
* The design uses a polished navy-blue system
* The website works on small phones, iPhone 16-sized devices, tablets, 1366×768 laptops, and large monitors
* The website opens securely from multiple countries
* Core functionality works on slow connections
* Forms are validated on the server
* Private submissions remain private
* Payment approval cannot accidentally create duplicate memberships
* Cloudinary or other media storage works correctly in production
* Deployment uses the correct Django WSGI entry point
* Production does not use `DEBUG=True`
* Tests pass
* Important URLs are preserved or redirected
* Sitemap and localized SEO are configured
* The admin workflow is practical and permission-controlled
* Backups and restore instructions are verified
* The finished website feels trustworthy, human, intuitive, and professionally designed

---

# 33. FINAL QUALITY STANDARD

Do not stop after making the website technically functional.

Review every page as:

* A first-time migrant seeking guidance
* A family member worried about fraud
* A Nepali-speaking visitor
* An English-speaking visitor
* A user on a low-cost Android phone
* A user outside Nepal
* An administrator managing hundreds of members
* A person using a keyboard or screen reader
* A visitor with a slow internet connection
* A search engine discovering the organization for the first time

Remove anything that feels:

* Confusing
* Unverified
* Decorative without purpose
* Repetitive
* Inaccessible
* Unprofessional
* Misleading
* Slow
* Fragile
* Generic
* Machine-generated

The final result should feel custom-built for this organization and its real community—not adapted from a generic nonprofit, consultancy, or migration template.

Make thoughtful decisions independently where requirements are obvious. Document important assumptions. Never invent organizational facts. Preserve real data above all else.
