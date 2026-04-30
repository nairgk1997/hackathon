# ResumeMatcher.jsx — Theme Changes

## Summary
Rethemed from a plain slate/white CSS-class-based design to match the Login.jsx sky/green design system.

## Changes Made

### Page Wrapper
- **Before:** `<div className="p-8 space-y-8">` — no background, no decoration
- **After:** Full-page gradient wrapper `min-h-screen bg-gradient-to-br from-sky-50 via-white to-green-50 relative font-sans` with two ambient glow blobs (sky left, green right), content constrained to `max-w-5xl mx-auto`

### Cards
- **Before:** `card` CSS class (generic white card)
- **After:** Inline `bg-white/90 backdrop-blur-sm rounded-2xl border border-sky-200/80 shadow-lg shadow-sky-900/10`

### Buttons
- **Before:** `btn-primary` CSS class
- **After:** Inline sky-to-green gradient — `bg-gradient-to-r from-sky-500 to-green-500 hover:from-sky-400 hover:to-green-400 text-white font-bold rounded-xl shadow-md shadow-sky-500/25 transition-all disabled:opacity-60 transform hover:-translate-y-0.5`

### Inputs / Select
- **Before:** `input` and `input max-w-xs` CSS classes
- **After:** Inline `px-4 py-3 rounded-xl bg-gray-50 border border-gray-200 focus:ring-2 focus:ring-sky-500 focus:border-sky-500 outline-none transition-all text-gray-900 font-medium placeholder:text-gray-400 text-sm`

### Drop Zone
- **Before:** `border-brand-500 bg-brand-50` / `hover:border-brand-400`
- **After:** `border-sky-500 bg-sky-50` / `hover:border-sky-400 hover:bg-sky-50/50`
- Upload icon color: `text-slate-400` → `text-sky-400`

### File List Items
- **Before:** `bg-slate-50 rounded-lg`
- **After:** `bg-sky-50/70 border border-sky-100 rounded-xl` with `text-sky-800 font-medium` filename

### CandidateCard
- **Before:** `card overflow-hidden` CSS class
- **After:** Same inline card token as above
- Rank badge: `text-slate-400` → `text-sky-400`
- Candidate name: `text-slate-800` → `text-sky-900`
- Sub-text / labels: `text-slate-400` → `text-sky-400`
- Vector score: `text-slate-600` → `text-sky-600`
- Expand button: `hover:bg-slate-100 text-slate-400` → `hover:bg-sky-50 text-sky-400`
- Username pill: `bg-slate-50 border-slate-200` → `bg-sky-50 border-sky-200`
- Summary italic text: `text-slate-600` → `text-sky-700/80`
- Alignment metrics grid background: `bg-slate-100 border-slate-100` → `bg-sky-100/50 border-sky-100`
- Metric cells: `bg-white` → `bg-white/80`, values `text-slate-700` → `text-sky-800`, labels `text-slate-400` → `text-sky-400`
- Detail section border: `border-slate-100` → `border-sky-100`
- Flag/detail body text: `text-slate-600` → `text-sky-700`
- Section label text: `text-slate-500` → `text-sky-500`
- Resume snippet bg: `bg-slate-50` → `bg-sky-50 rounded-lg`

### Page Heading
- h1: `text-slate-900` → `text-sky-950 font-extrabold tracking-tight`
- Subtitle: `text-slate-500` → `text-sky-700/70 font-medium`

### Results Section
- Domain label: `text-brand-600` → `text-sky-600`
- Empty state: `text-slate-500` → `text-sky-500`
- Section h2: `text-slate-800` → `text-sky-900`
- Sub-text: `text-slate-400` → `text-sky-400`
