# Coding Frame — Q40 "Expectations / concerns about using an AI mental-health chatbot"

**Status:** Illustrative reference frame, derived inductively from the 110 open-ended
responses to Q40. It is designed to *stand in for* the dissertation's Framework Analysis
coding frame so the calibration pipeline can be demonstrated end-to-end. To run the
pipeline on the real study, replace the `manual_theme` column of the reference set with
the author's own Framework Analysis codes — no other change is required.

**Unit of analysis:** one free-text response.
**Decision rule:** assign the **single dominant theme** — the concern the respondent
gives most weight to (stated as their "main concern", placed first, or given the most
words). Responses are frequently multi-theme; the dominant-theme rule is what makes the
task hard enough to be worth testing a prompt against.

---

## Themes

### 1. PRIVACY — Privacy & data security
Concern that personal/sensitive disclosures are not confidential: leaks, hacking,
selling or storing data, information "no longer yours".
**Markers:** *confidential, data, leaked, sold, hacked, stored, breach, private.*
> "Providing your information to an online AI chatbot means personal data is no longer yours and can be repeated anywhere."

### 2. ACCURACY — Accuracy & reliability of information
Concern that the advice/information is wrong, made up (hallucinated), generic,
inconsistent, scraped from unreliable web sources, or simply not effective.
**Markers:** *wrong, inaccurate, made up, generic, unreliable, effective, from the web.*
> "AI has a tendency to make things up and bring up inaccurate information."

### 3. EMPATHY — Empathy gap / lack of human connection
Concern that the system cannot genuinely feel, understand, or emotionally connect;
reads no non-verbal cues; is impersonal/robotic; that people need human-to-human
connection to open up.
**Markers:** *not real, robot, can't feel/understand, non-verbal, impersonal, generic answer, human connection.*
> "Most people need human-to-human connection to open up."

### 4. SAFETY — Safety & safeguarding
Concern about **harm to vulnerable users**: sycophancy / reinforcing harmful behaviour,
failure to detect or escalate a crisis, triggering, unhealthy dependency or attachment,
danger to life.
**Markers:** *crisis, harm, self-harm, vulnerable, dependency, attachment, trauma, sided with, loss of life.*
> "It couldn't determine if I was entering a crisis and has in the past pushed me into a crisis situation."

### 5. ACCOUNTABILITY — Professional accountability, training & regulation
Concern that the system lacks clinical training, qualification, regulation, oversight,
or the authority/responsibility to provide care.
**Markers:** *not regulated, no training, unqualified, no authority, can't be held responsible.*
> "They are not regulated in terms of what they can say for mental-health support."

### 6. ACCESS_BENEFIT — Access & practical benefits (positive)
A **positive** expectation: affordability, 24/7 availability, no waiting lists, speed,
non-judgemental, tailored/reassuring. Coded as dominant only when the benefit *is* the
response's main point (rare in a concerns question — a deliberate stress-test for the model).
**Markers:** *cheap, free, 24/7, quick, no waiting list, less judgemental, accessible.*
> "It's a cheaper option for individuals who cannot afford therapy."

### OTHER
Substantive content that does not fit the six themes (e.g. pure signposting/role-boundary
concerns). Used sparingly.

---

## Notes for the rater / model
- Positive **and** negative content in one response → code the **concern** (this is a
  concerns question), unless the respondent explicitly foregrounds the benefit.
- "Doesn't understand me / no non-verbal cues" → EMPATHY, unless it is framed as a
  *safety* failure (missing a crisis) → SAFETY.
- "Wrong advice that could cause harm" → ACCURACY if the emphasis is *wrongness*; SAFETY
  if the emphasis is *harm to a vulnerable person*.
- "Won't keep my data private *because* it isn't a trained professional" → whichever the
  respondent foregrounds; ACCOUNTABILITY if the lack of training is the causal core.
