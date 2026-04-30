# CandidateDashboard.jsx — Theme Changes

## Summary
Rethemed from a full dark (`bg-slate-900`) design to the sky/green light theme matching Login.jsx. Pipeline stage cards, header, and status indicators all updated to the light palette.

## Changes Made

### Page Wrapper
- **Before:** `min-h-screen bg-slate-900 text-white`
- **After:** `min-h-screen bg-gradient-to-br from-sky-50 via-white to-green-50 font-sans` with fixed ambient glow blobs (sky left, green right)

### Header
- **Before:** `border-slate-700/60 bg-slate-900/80 backdrop-blur sticky top-0`
- **After:** `border-sky-200 bg-white/80 backdrop-blur-sm sticky top-0`
- Logo: plain `Briefcase text-brand-500` → `Leaf` icon in `from-sky-600 to-green-600` gradient container (matching Login.jsx navbar)
- "Candidate Portal" label: `text-slate-400` → `text-sky-500 font-semibold`
- Welcome heading: `text-white` → `text-sky-950 font-bold`
- Sign out button: `text-slate-400 hover:text-white` → `text-sky-600 hover:text-sky-900 hover:bg-sky-50 rounded-lg`

### Status Pill
- **Before:** `bg-slate-800 text-slate-300 ring-1 ring-slate-700`
- **After:** `bg-sky-100 text-sky-700 border border-sky-200 shadow-sm` with a live green pulse dot (matching Login.jsx's AI-Powered badge)

### Pipeline Stage Cards

#### Active state
- **Before:** `bg-slate-800 border-transparent` with per-color glow shadow (dark/opaque)
- **After:** `bg-white/95 border-sky-200` with per-color glow shadow (lighter, appropriate for light bg)

#### Done state
- **Before:** `bg-slate-800/50 border-slate-700 hover:border-slate-600`
- **After:** `bg-white/70 border-sky-100 hover:border-sky-200 hover:shadow-lg`

#### Locked state
- **Before:** `bg-slate-800/20 border-slate-800/50 opacity-40`
- **After:** `bg-sky-50/40 border-sky-100/50 opacity-50`

### Stage Connector Line
- **Before:** `bg-slate-700`
- **After:** `bg-sky-200`

### Stage Icon Bubble
- Active: per-color `bg-{color}-500/20 text-{color}-400` (dark tint) → `bg-{color}-100 text-{color}-600` (light tint)
- Done: `bg-emerald-500/15 text-emerald-400` → `bg-emerald-100 text-emerald-600`
- Locked: `bg-slate-700/30 text-slate-600` → `bg-sky-100/50 text-sky-300`

### Stage Title
- **Before:** `text-white` (active/done) / `text-slate-600` (locked)
- **After:** `text-sky-950` (active/done) / `text-sky-400/60` (locked)

### Stage Description
- **Before:** `text-slate-400` (active/done) / `text-slate-700` (locked)
- **After:** `text-sky-700/70` (active/done) / `text-sky-400/40` (locked)

### "Completed" Badge
- **Before:** `bg-emerald-500/10 text-emerald-400 border-emerald-500/20`
- **After:** `bg-emerald-50 text-emerald-700 border border-emerald-200 font-semibold`

### "Action Required" Badge
- Per-color: dark `bg-{color}-500/15 text-{color}-400 border-{color}-500/40` → light `bg-{color}-100 text-{color}-700 border-{color}-300`

### CTA Start Button
- Per-color: solid `bg-{color}-600 hover:bg-{color}-700` → `bg-gradient-to-r` with softer shadow

### Locked Icon
- **Before:** `text-slate-700`
- **After:** `text-sky-300`

### colorMap — "blue" renamed to "sky"
- Stage 2 color key: `'blue'` → `'sky'` for semantic consistency with the sky design system

### Footer Note
- **Before:** `text-slate-600`
- **After:** `text-sky-400 font-medium`
