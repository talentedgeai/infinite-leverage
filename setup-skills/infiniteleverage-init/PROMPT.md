# The workshop prompts (canonical)

This file is the single source of the four build-session prompts. The workshop page renders this file; it never owns its own copy. Edit here, release, and the page follows.

CI checks this file against `SKILL.md`: every catalog key the Block I prompt writes as `[pending]` must appear in the skill's Stage F fill list, and the Block II prompt's guide URL must point at the `stable` branch.

All four are pasted into the **Code tab of Claude Desktop**. Not the Chat tab: the first prompt writes real files, and every block after it runs commands.

The only prerequisite no prompt can cover is Claude Desktop being installed and signed in, because until then the prompt has nowhere to run. Windows PC owners should do the Ubuntu turn-on as prework; the setup checks for it either way.

---

## I.1 Bootstrap and interview

Creates `~/code-projects/<slug>/`, writes the project catalog, runs the eight-question interview, and writes the product plan as markdown and HTML.

```
You're my product partner for the Infinite Leverage retreat today. You run the interview and produce the files below.

Act as Dan Shipper for this session. That means: start from the outcome I'm trying to create, not the features. Name who each thing is for. Cut anything that isn't load-bearing. Refuse to let "done" be a vibe. Every build block you write must state a Goal, a Definition of Done I can literally check off, and Success Criteria I can measure. If something in my answers is vague, push back once and get specific before you write the plan. Keep the language plain and confident. No filler.

We'll go in three steps: set up your workspace, talk through a few questions about your business, then write your plan. I'll handle all the technical parts. You just answer in plain English.

STEP 1: Set up the workspace.

First, ask me one question and wait for my answer:
"What's your business name?"

Take my answer and turn it into a short, lowercase, dash-separated slug. Then create:
- ~/code-projects/<slug>/
- ~/code-projects/<slug>/Working Files/

Use exactly that location. The setup prompt in Block II builds into the same folder, so the path has to match.

Write ~/code-projects/<slug>/CLAUDE.md (create or overwrite) with EXACTLY this content between the BEGIN and END markers. Do not modify, summarize, or abbreviate it:

----------BEGIN CLAUDE.md----------
# Project Catalog

## Core stack (filled by the Block II setup prompt): Build 1 needs all of these
- IL skill installed: [pending]
- GitHub repo: [pending]
- Vercel project: [pending]
- Site live at: [pending]
- Supabase project: [pending]
- Supabase URL: [pending]
- Supabase keys: [pending]

## Email and domain (set up during Build 2): Build 1 does NOT need these
- Resend account: [deferred to Build 2]
- Sending domain verified: [deferred to Build 2]
- Custom domain live: [deferred to Build 2]

## Build
- Build 1 status: [pending]
- Admin account seeded: [pending]
- Build 2 status: [pending]

# How to use this catalog

You are my engineering partner. Before any task or /goal command:
1. Read this entire CLAUDE.md AND Working Files/product-plan.md.
2. Identify which catalog and plan items the task requires.
3. If a required item is still [pending], STOP and tell me what to fill in.
   Use plain English: "I need X to do this. Please Y."
4. Don't proceed until every required item is filled. Anything marked
   [deferred to Build 2] never blocks Build 1.
5. After the task succeeds, update the catalog with the new state.

NEVER write a secret into this file. Keys live in website/.env.local only.
Catalog lines about keys record status, for example
"stored in website/.env.local", never the value itself.

Required items by task:
- /goal build 1 → product-plan.md complete + Core stack complete
- /goal build 2 → the above + Build 1 complete + Email and domain complete
- Any deploy → GitHub repo + Vercel project wired
----------END CLAUDE.md----------

Once both folders exist and CLAUDE.md is written with the exact content above, tell me it's done and move on.

STEP 2: A few questions about your business.

Ask these eight questions one at a time. Keep it light and conversational. Don't move on until I've answered each one. The first two set the direction for everything else, so listen closely and push back once if my answer is vague.

1. Walk me through what happens right now when someone wants to work with you. Where do leads go cold, get forgotten, or slip through the cracks?

2. Ninety days after this is live, what has to be true for you to call it a win? And roughly how many inquiries come in a week?

3. What do you sell?

4. What kinds of inquiries come in? Give me 2 to 5 types. Think about the different reasons people reach out, for example: general questions, coaching, keynote bookings, quote requests, or support. These become the categories your leads get sorted into, so use whatever words match how you actually think about your business.

5. What look and feel do you want? Pick one:
A) MINIMALIST APPLE: clean, lots of white space, calm, premium.
B) BOLD FERRARI: high contrast, confident, energetic, strong color.
C) ACADEMIC: serious, structured, editorial, trustworthy.

6. Do you have brand colors? If yes, paste your hex codes (I need at least the main one; an accent color and a background color are optional). If you don't have them, just say "use the design system defaults" and I'll pick colors that fit the look you chose.

7. When someone becomes a contact, what extra details do you want to remember about them?

Think about the notes you'd jot down on a business card or in your phone. Pick up to three things that matter for your business. For each one, just tell me the detail and roughly what kind of answer it holds:
- A short typed note (for example: "How we met" or "Referred by")
- A pick-from-a-list choice (for example: "Membership tier" with options Gold, Silver, Bronze, or "Industry" with options you list)
- A date (for example: "Renewal date" or "Last event attended")

You don't need to overthink this. If nothing comes to mind, two simple ones are plenty. Examples to spark ideas: company size, how they heard about you, deal value, region, or anniversary date.

8. Do you already own a web address (domain) for this? If yes, tell me what it is. If not, just say "not yet". We buy and connect it later today, in Build 2, and nothing before that depends on it.

STEP 3: Once I've answered everything.

Write my product plan to Working Files/product-plan.md with EXACTLY this structure, dropping my interview answers in wherever you see [bracketed values]. Keep the technical brief and data model exactly as written; your Dan Shipper judgment goes into the framing and the two build blocks, which must each carry a real Goal, Definition of Done, and Success Criteria.

----------BEGIN product-plan.md----------
# Product plan · [my business]

## What we're actually building and why

In one sentence: [Dan Shipper voice. Use my answer to Q1 (what's broken
today) and Q3 (what I sell) to state the outcome this CRM creates for me,
in terms of what I can do after it exists that I can't do today. Tie it to
the gap I named in Q1. Not "a CRM" but what the CRM lets me do.]

Who it's for: [me as the operator, plus the kind of person who fills out
my form, drawn from Q3 and Q4.]

What we are deliberately NOT building: no affiliates, no subscriptions,
no cohorts, no analytics dashboards, no integrations beyond what's named
here. If it isn't load-bearing for capturing and working a lead, it's out.

## The brief (drives every /goal command)

You are my engineering partner for building my CRM today. Build a
Next.js (App Router) + Supabase + Vercel app with two surfaces:
a public marketing site that captures leads, and an /admin CRM.
The /admin section is open and unprotected at first; it gets locked
down with email-and-password Supabase Auth later in the build. Do
not add any auth, login page, or route protection until I explicitly
ask for it.

The CRM has exactly four parts:

- People: a contact directory, one row per person, deduplicated by
email. Columns: id, email (unique), name, phone, company, role,
source_site, ok_to_contact, attributes (jsonb), created_at,
updated_at. The custom attributes I named go inside attributes.
The keys are my attribute names and the values match the types I
specified.

- Contacts: an inquiry pipeline. Each inquiry links to a person and
moves through stages new_lead, contacted, discovery_call,
proposal, won, lost. Columns: id, person_id, type, subject,
message, source, status, metadata (jsonb), created_at. The type
field is constrained to exactly the inquiry types I gave in Q4
(lowercased).

- activity_log: every status change on a Contacts row writes one row
here. Columns: id, contact_id, person_id, from_status, to_status,
actor, note, created_at.

- Orders: what people bought. Columns: id, person_id, product_name,
amount_cents, currency, status (pending, paid, refunded,
cancelled), created_at.

- Newsletter: people who opted in to email, tracked by
people.ok_to_contact = true. No separate table.

Conventions:
- Upsert people by email; never duplicate a person.
- Access Supabase server-side with the secret key; never expose
secrets to the client; keys live in website/.env.local and in the
hosting environment only, never in CLAUDE.md and never in git.
- Keep it simple: no affiliates, no subscriptions, no cohorts.
- Work one step at a time and wait for my approval before each step.

My business: [Step 1 name + Q3 what I sell]
My inquiry types (contacts.type enum): [Q4 answer]
My design system: [Q5 answer, one of Minimalist Apple / Bold Ferrari / Academic]
My brand colors: [Q6 answer]
My custom attributes (people.attributes jsonb keys): [Q7 answer, up to three with type]
My domain: [Q8 answer, or "not yet, buying in Build 2"]

## BUILD 1: Prove the loop

Goal: A stranger can submit an inquiry on my live site and I can see
that lead inside /admin, on the same day, without anyone touching the
database by hand. This closes the exact gap I named in Q1. It is the
smallest thing that proves the whole system works end to end. Nothing
else matters until this is real.

Scope: the People and Contacts tables with my custom attributes wired
into the jsonb column; a working contact form on the live marketing
site that writes a People row (upserted by email) and a linked Contacts
row; one admin login with a single verified account; one admin page
that lists incoming leads newest first.

Definition of Done (every box must be true):
- The contact form is live on my project's public web address, the one
the setup prompt put online, not localhost. (My own domain comes in
Build 2; nothing in Build 1 waits for it.)
- Submitting it creates exactly one People row and one linked Contacts
row, deduplicated by email on repeat submits.
- My chosen custom attributes are saved correctly inside attributes.
- A new Contacts row lands in status new_lead.
- I can log in to /admin with my one seeded account.
- The admin leads page shows the submission within seconds, newest first.
- I personally run the full flow once: submit as a visitor, log in, see it.

Success Criteria (how we know it's good, not just done):
- From a cold start, I can go submit to visible in under 60 seconds.
- Two submissions from the same email produce one person, not two.
- I can read the lead's name, type, message, and my custom attributes
on the admin page without opening Supabase.
- No lead can land and go unseen, which is the failure mode I named in Q1.

## BUILD 2: Make it the system I run the business from

Goal: Turn the proven loop into the place I actually manage relationships
and money, on my own web address. After this, I work leads, record what
people bought, and keep my newsletter list entirely from /admin behind my
login, every new lead gets an automatic confirmation email, and the whole
thing lives at my domain. This is what makes my Q2 ninety-day win
achievable.

Scope: the rest of the /admin back end behind my login: the full People
directory, all inquiries with working pipeline stages, the Orders list,
and the Newsletter list (ok_to_contact = true). Plus Resend wired so a
confirmation email fires on form submit, and my custom domain bought (if
I don't have one) and pointed at the site. Every Contacts status change
writes an activity_log row.

Definition of Done (every box must be true):
- All four parts (People, Contacts, Orders, Newsletter) are visible and
usable in /admin, and all of /admin sits behind my login.
- I can move a Contacts row through new_lead to contacted to
discovery_call to proposal to won or lost from the interface.
- Each status change writes one activity_log row with from_status,
to_status, and actor.
- The People directory is searchable and shows my custom attributes.
- I can add an Orders row against a person and see it on their record.
- The Newsletter list shows everyone with ok_to_contact = true.
- Resend is connected, the sending domain is verified, and a real
confirmation email arrives after a form submit.
- My site answers on my own domain.

Success Criteria (how we know it's good, not just done):
- I can run a lead from first inquiry to won without leaving /admin or
touching the database.
- A person's full history (their inquiries, status changes, and orders)
is visible in one place.
- A test submission produces a confirmation email in the inbox, not spam,
with my domain as the sender.
- Nothing in /admin is reachable without logging in.
- At my real inquiry volume from Q2, this keeps up without me dropping
to the database by hand.
----------END product-plan.md----------

Then write a second copy of the exact same plan to
Working Files/product-plan.html as a nicely formatted, self-contained
HTML file I can open in a browser or hand to someone. Rules for the HTML:
- One file, no external dependencies. All CSS inline in a <style> block.
No frameworks, no CDN links, no JavaScript.
- Use the Inter font (with a system-font fallback) and a readable
centered column around 880px wide.
- Style it to match my Q5 design system and my Q6 brand colors. If I said
"use the design system defaults," pick a clean palette that fits the
look I chose.
- Render the structure clearly: a title, the "what we're building and why"
section, my interview answers as a clean key-value summary, and the two
build blocks with Goal, Definition of Done, and Success Criteria. Show
the Definition of Done and Success Criteria as proper checklists.
- No gradients anywhere. No gradient text, no gradient backgrounds, no
gradient effects.
- The content must match product-plan.md exactly. The HTML is a formatted
view of the same plan, not a different or shortened one.

Then:
- Tell me my project folder path.
- Tell me both files were written: product-plan.md and product-plan.html.
- Tell me I'm ready for Block II.
```

---

## II.1 Install the stack

The whole of Block II in one paste: the triage forks, the guide, the human gates, and the graduation lap that proves the setup works before anyone depends on it.

```
I'm setting up the Infinite Leverage stack, and I'm not technical.

Fetch and follow this guide exactly:
https://raw.githubusercontent.com/talentedgeai/infiniteleverage-8-agents-template/stable/setup-skills/infiniteleverage-init/SKILL.md

Before the guide, three checks in this order:

1. Where you are. If you can run commands on this machine, continue here.
   If you can't, because I pasted this into a chat with no computer access,
   assume this machine can't be set up directly and walk me through the
   guide's cloud track in my browser instead.

2. What this machine is. Detect Mac or Windows yourself, don't ask. If
   Windows, ask me one question: is this my own computer, or one my
   company manages? My own means the guide's Ubuntu path. Company-managed
   means no local install at all: check this browser can reach claude.ai
   and github.com, and if it can, follow the cloud track; if it can't,
   stop and tell me plainly that I need a loaner or a personal machine.

3. What's already here. If you find a previous setup, show me what you
   found in plain English and ask me one question: keep building on it,
   or start fresh alongside it. Never delete anything either way.

Then follow the guide. Do every step a computer can do yourself. When you
reach a step marked "Your turn", tell me what to click in numbered steps
and, in one sentence, why you can't do it for me, then wait, and verify
with a real check before moving on. Plain English, one step at a time.

Never write a secret into any file except website/.env.local. Before you
finish, prove the setup works by yourself: run a test change to the
database with no dashboard, and open, merge, and watch a test change
deploy to my live site. Then fill every [pending] line in the Core stack
section of my project's CLAUDE.md, and tell me in plain English what you
can now do for me without asking.
```

### Page copy that surrounds this prompt

**Before you start:** install Claude Desktop and sign in. On a Windows PC, do the ten-minute Ubuntu turn-on first. On a company-managed laptop, say so when asked; the setup runs in the browser instead.

**The six moments the attendee is asked to act:** the permission decision, creating the three accounts, the sign-in and Authorize clicks, any two-factor code, the one Vercel import click, and on Windows an administrator click plus a restart. Each is shown with the reason it cannot be Claude.

**No money moves in this block.** Buying a web address happens in Block IV and is always the attendee's click.

**How they know it worked:** the graduation lap. A database change with no dashboard, then a pull request opened, merged, watched to a green build, and the live site updating.

---

## III.1 /goal build 1

Gated on the Core stack only. Anything marked `[deferred to Build 2]` must not block this build.

```
Read CLAUDE.md and Working Files/product-plan.md first. Verify that
product-plan.md is complete and that the Core stack section of CLAUDE.md
has no [pending] values. Ignore anything marked [deferred to Build 2]:
email and my own domain are not needed for this build. If a core item is
missing, stop and tell me what to fill in, in plain English.

/goal Look at my product plan in Working Files and execute BUILD 1.
Build the data model (People, Contacts, and my custom attributes), a
contact form on my live site, an admin login and password, and ONE
admin page behind that login where I can see the leads that come in.
Set up and verify one admin account so I can actually sign in.
Work until you are done. When finished, give me a short summary of
everything you built and the links I need to test it.

Then walk me through testing it myself: I submit the form as a stranger,
log in, and see my own lead on the admin page.

After that passes, update the Build section of CLAUDE.md:
- Build 1 status: done
- Admin account seeded: done, with email [my admin email]
```

---

## IV.1 /goal build 2

Where email and the domain enter, deliberately last, because three of the four remaining human steps involve an inbox, a registrar login, or the attendee's money.

```
Read CLAUDE.md and Working Files/product-plan.md first. Verify that
Build 1 is done and the Core stack has no [pending] values. If not, stop
and tell me what is missing.

This build needs two things set up that we deliberately left until now.
Walk me through each one before building, one step at a time, telling me
what to click and why you can't do it for me:

1. A Resend account and a verified sending domain, so my confirmation
   emails come from my address and land in inboxes rather than spam.
2. My own web address. If I already own one, help me point it at my
   site. If I don't, tell me what to buy and where, and let me make the
   purchase myself. Never buy anything on my behalf.

As each one is done, verify it with a real check, and record it in the
Email and domain section of CLAUDE.md. Record status only, never a key.

/goal Then look at my product plan in Working Files and execute BUILD 2.
Build the rest of the /admin back end behind my login: the full People
directory, all inquiries, and a pipeline to move each inquiry through
its stages, plus the Orders list and the Newsletter list. Wire Resend so
that when someone submits the contact form they get a confirmation email
and I get a notification. Keep it consistent with my design system.
Work until you are done, then give me a short summary and the links to
test each screen and the email.

After you finish, update the Build section of CLAUDE.md:
- Build 2 status: done
```

---

## Known gap

The Block II prompt fetches the setup guide from the `stable` branch of the canonical repo. That branch does not exist until the v2 skill is released and the release workflow starts fast-forwarding it. Until then the URL returns 404, and the published page says so at the top. Creating `stable` is part of shipping the skill, not a separate task.
