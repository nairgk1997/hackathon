# Login Page — `Login.jsx`

## Overview

`Login.jsx` serves as both the **landing/home page** and the **authentication entry point** for the Hire AI platform. It is exported as `Home` and is the default route (`/`).

---

## Layout Structure

```
Home (full-screen)
├── Background decorative elements (glows, floating shapes)
├── <nav>        — Logo + "Login to Portal" button
├── <header>     — Hero section (headline + subtext)
├── <section>    — Services grid (6 flip-card leaflets)
└── Login Modal  — Conditionally rendered overlay
```

---

## Hero Section

| Element | Content |
|---|---|
| Badge | "AI-Powered Hiring Platform" (violet pill with ping dot) |
| Headline | "Hire Smarter. Build Stronger Teams." |
| Gradient accent | `violet-600 → fuchsia-500 → rose-500` |
| Subtext | "Automate interviews, screen resumes, and evaluate candidates in real time…" |

**Color scheme:** Violet / Fuchsia / Rose — changed from the original sky-blue to a more distinctive gradient identity.

---

## Services Grid

Six flip-card tiles rendered from the `services` array. Each card has:

- **Front face** — icon + service title + "Explore Inside" label; rotates on hover via CSS 3D perspective transform (`rotateY(-105deg)`)
- **Back face** — title, description, and feature checklist; fades in on hover

| Service | Icon |
|---|---|
| AI Video Interviewer | `Video` |
| AI Phone Screener | `Phone` |
| AI Resume Screener | `FileText` |
| AI Coding Interviewer | `Code` |
| English Proficiency | `Globe` |
| Virtual Platform | `Users` |

---

## Login Modal

Triggered by the "Login to Portal" nav button. Two-panel layout (desktop):

### Left panel
- Background image with overlay
- Brand copy: "Cultivate Great Talent."

### Right panel — Form

| Field | Type | Notes |
|---|---|---|
| Login type toggle | UI toggle | `candidate` or `admin` |
| Username | `text` | Maps to `username` state |
| Password | `password` | Maps to `password` state |
| Remember me | checkbox | UI only, no persistence |
| Forgot Password | link | UI only, no handler |
| Google SSO button | button | UI only, not wired |

### Auth Flow

```
POST /auth/login  { username, password }
  ↓ success
  localStorage.setItem('hire_ai_auth', 'true')
  localStorage.setItem('hire_ai_role', data.role || loginType)
  ↓ redirect
  hr_manager / admin  →  /jd
  candidate           →  /assessment
```

Error state is shown inline below the password field on failed login.

---

## State

| State | Type | Purpose |
|---|---|---|
| `isLoginModalOpen` | boolean | Controls modal visibility |
| `loginType` | `'candidate' \| 'admin'` | Selected role tab |
| `username` | string | Controlled input |
| `password` | string | Controlled input |
| `error` | string | Auth error message |
| `loading` | boolean | Disables submit during request |

---

## Recent Changes

- **Hero text updated:** Headline rephrased to "Hire Smarter. Build Stronger Teams." with a violet-to-rose gradient accent.
- **Color scheme updated:** Hero badge and gradient shifted from sky-blue to violet/fuchsia/rose.
- **Removed:** "Interactive / Hover Over Leaflets" section label above the services grid.
