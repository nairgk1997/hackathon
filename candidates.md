# Candidates.jsx — Theme Changes

## Summary
Rethemed from a plain slate/brand CSS-class-based design to match the Login.jsx sky/green design system. Covers the main page, stats cards, data table, skeleton loader, empty state, and the InterviewReportModal.

## Changes Made

### Page Wrapper
- **Before:** `<div className="p-8 space-y-6">` — no background
- **After:** Full-page `min-h-screen bg-gradient-to-br from-sky-50 via-white to-green-50 relative font-sans` with two ambient glow blobs (sky left, green right), content constrained to `max-w-screen-xl mx-auto`

### Page Header
- h1: `text-slate-900` → `text-sky-950 font-extrabold tracking-tight`
- Subtitle: `text-slate-500` → `text-sky-700/70 font-medium`
- Refresh button: `btn-secondary` CSS class → inline `text-sky-700 bg-white border border-sky-200 rounded-xl hover:bg-sky-50 shadow-sm`

### Stats Cards
- **Before:** `card p-4` CSS class
- **After:** Inline `bg-white/90 backdrop-blur-sm rounded-2xl border border-sky-200/80 shadow-lg shadow-sky-900/10 p-4`
- Total stat color: `text-slate-800` → `text-sky-800`
- Stat labels: `text-slate-400` → `text-sky-400 font-medium`
- `Applied` status badge: `bg-slate-100 text-slate-600 border-slate-200` → `bg-sky-100 text-sky-600 border-sky-200`

### Table Card
- **Before:** `card overflow-x-auto` CSS class
- **After:** Inline card token with `overflow-x-auto`

### Table Header
- Background: `bg-slate-50/95` → `bg-sky-50/95`
- Border: `border-slate-200` → `border-sky-200`
- Column labels: `text-slate-400/500` → `text-sky-500`

### Table Rows
- Dividers: `divide-slate-100` → `divide-sky-100`
- Hover: `hover:bg-blue-50/40` → `hover:bg-sky-50/50`
- Expanded row bg: `bg-blue-50/60` → `bg-sky-50/60`
- Candidate name: `text-slate-800` → `text-sky-900`
- Email / metadata: `text-slate-400` → `text-sky-400`
- Job ID: `text-slate-500` → `text-sky-500`
- Empty dash: `text-slate-300` → `text-sky-200`

### Credentials Cell
- Username pill: `bg-slate-100 border-slate-200 text-slate-700` → `bg-sky-50 border-sky-200 text-sky-700`
- Password pill: `bg-amber-50 border-amber-200` unchanged (semantic color)

### Action Buttons
- Shortlist link: `text-blue-600 hover:text-blue-700` → `text-sky-600 hover:text-sky-700`
- Awaiting test: `text-slate-400` → `text-sky-400`
- View Report: `text-brand-600 bg-brand-50 border-brand-200` → `text-sky-600 bg-sky-50 border-sky-200 hover:bg-sky-100`
- Details toggle (collapsed): `bg-white border-slate-200 text-slate-500 hover:bg-slate-50` → `bg-white border-sky-200 text-sky-500 hover:bg-sky-50`
- Details toggle (expanded): `bg-slate-100 border-slate-300 text-slate-700` → `bg-sky-100 border-sky-300 text-sky-700`

### Expandable Detail Row
- Row bg: `bg-slate-50 border-slate-200` → `bg-sky-50/50 border-sky-100`
- Section labels: `text-slate-500` → `text-sky-500`
- Reasoning box: `bg-white border-slate-200 text-slate-700` → `bg-white border-sky-100 text-sky-800`
- Log items: `bg-white border-slate-200 text-slate-600` → `bg-white border-sky-100 text-sky-700`
- Log chevron: `text-slate-400` → `text-sky-400`

### SkeletonTable
- Header: `bg-slate-50/95 border-slate-200 text-slate-400` → `bg-sky-50/95 border-sky-200 text-sky-400`
- Row dividers: `border-slate-100` → `border-sky-100`
- Skeleton bars: `bg-slate-200/bg-slate-100` → `bg-sky-100/bg-sky-50`

### ScoreBar (Pending state)
- **Before:** `text-slate-400 bg-slate-100 border-slate-200` with `bg-slate-300` dot
- **After:** `text-sky-400 bg-sky-50 border-sky-200` with `bg-sky-300` dot

### EmptyState
- Icon container: `bg-slate-100` → `bg-sky-100/80`
- Icon: `text-slate-300` → `text-sky-300`
- Badge: `bg-slate-200` → `bg-sky-200`, text `text-slate-400` → `text-sky-500`
- Heading: `text-slate-500` → `text-sky-600`
- Body: `text-slate-400` → `text-sky-400`

### InterviewReportModal
- Backdrop: `bg-black/50 backdrop-blur-sm` → `bg-sky-950/40 backdrop-blur-md`
- Modal border: none → `border border-sky-100`
- Modal shadow: `shadow-2xl` → `shadow-2xl shadow-sky-900/20`
- Header border: `border-slate-100` → `border-sky-100`
- Title: `text-slate-900` → `text-sky-950`
- Subtitle: `text-slate-500` → `text-sky-500`
- Close button: `hover:bg-slate-100 text-slate-400 hover:text-slate-600` → `hover:bg-sky-50 text-sky-400 hover:text-sky-600`
- Loading spinner/text: `text-slate-400` → `text-sky-400`
- Pending verdict bg: `bg-slate-50 border-slate-200` → `bg-sky-50 border-sky-200`
- Pending verdict text/icon: slate → sky
- Recommendation reason text: `text-slate-600` → `text-sky-700/80`
- AI Summary box: `bg-slate-50 border-slate-200` → `bg-sky-50/70 border-sky-100`
- Integrity score badge: `bg-slate-100 text-slate-600` → `bg-sky-100 text-sky-700 border-sky-200`
- Proctoring log items: `bg-slate-50 border-slate-200 text-slate-600` → `bg-sky-50 border-sky-100 text-sky-700`
- Empty proctoring box: `bg-slate-50 border-slate-200 text-slate-400` → `bg-sky-50/70 border-sky-100 text-sky-400`
- Footer border: `border-slate-100` → `border-sky-100`
- Close button: `btn-secondary` CSS class → inline `text-sky-700 bg-white border border-sky-200 rounded-xl hover:bg-sky-50`

### SectionHeader helper
- Container text: `text-slate-700` → `text-sky-700`
- Icon: `text-slate-400` → `text-sky-400`

### SummaryBody helper
- Body text: `text-slate-700` → `text-sky-800`
- Bullet dot: `text-slate-400` → `text-sky-400`
