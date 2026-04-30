# JDGenerator.jsx — Theme Changes

## Summary
Rethemed from a plain slate/brand CSS-class-based design to match the Login.jsx sky/green design system. All sub-components (StepIndicator, Step1, Step2, Step3, DirectUploadForm) were updated.

## Changes Made

### Page Wrapper
- **Before:** `<div className="p-8">` — no background, no decoration
- **After:** Full-page gradient wrapper `min-h-screen bg-gradient-to-br from-sky-50 via-white to-green-50 relative font-sans` with two ambient glow blobs (sky left, green right), content constrained to `max-w-4xl mx-auto`

### Page Heading
- h1: `text-slate-900` → `text-sky-950 font-extrabold tracking-tight`
- Subtitle: `text-slate-500` → `text-sky-700/70 font-medium`

### Mode Toggle (AI Generate / Direct Upload)
- **Before:** Active state `bg-brand-600 text-white border-brand-600`, inactive `text-slate-600 border-slate-300 hover:border-brand-400`
- **After:** Active state `bg-gradient-to-r from-sky-500 to-green-500 text-white border-sky-500 shadow-md shadow-sky-500/25`, inactive `text-sky-600 border-sky-200 hover:border-sky-400 hover:bg-sky-50`
- Border radius: `rounded-lg` → `rounded-xl` to match card language

### StepIndicator
- Active step circle: `bg-brand-600` → `bg-sky-600`
- Inactive step circle: `bg-slate-200 text-slate-500` → `bg-sky-100 text-sky-400`
- Done step: `bg-green-500` unchanged
- Active label: `text-slate-800` → `text-sky-900`
- Inactive label: `text-slate-400` → `text-sky-400`
- Chevron separator: `text-slate-300` → `text-sky-300`

### Step 1 — Role Intent
- h2: `text-slate-800` → `text-sky-900`
- Description: `text-slate-500` → `text-sky-600/80`
- Textarea: `input` CSS class → inline sky-focused input token

### Step 2 — Answer Questions
- h2/description: slate → sky colors
- Question cards: `card p-4` → inline `bg-white/90 backdrop-blur-sm rounded-2xl border border-sky-200/80 shadow-lg shadow-sky-900/10 p-4`
- Question text: `text-slate-700` → `text-sky-800`
- Question number accent: `text-brand-600` → `text-sky-600`
- Read-aloud button: `text-slate-400 hover:text-brand-600 hover:bg-brand-50` → `text-sky-400 hover:text-sky-600 hover:bg-sky-50`
- Answer input: `input flex-1` CSS class → inline sky-focused input token

### Step 3 — Review & Save
- h2/description: slate → sky colors
- JD preview card: `card p-6` → inline card token
- JD title: `text-slate-900` → `text-sky-950`
- Experience level badge: `bg-brand-100 text-brand-700` → `bg-sky-100 text-sky-700 border border-sky-200`
- JD body text: `text-slate-600` → `text-sky-700/80`
- Skills label: `text-slate-500` → `text-sky-500`
- Skill pills: `bg-slate-100 text-slate-700` → `bg-sky-50 text-sky-700 border border-sky-200`

### DirectUploadForm
- h2/description: slate → sky colors
- Form labels: `text-slate-700` → `text-sky-800` with `text-xs font-bold ml-1` styling matching Login.jsx form labels
- All inputs/textarea/select: `input w-full` CSS class → inline sky-focused input token
- Helper text: `text-slate-400` → `text-sky-400`
- Error message: plain `text-red-600` → `text-red-600 bg-red-50 border border-red-100 rounded-xl px-4 py-2.5` (matching Login.jsx error style)
- "Upload Another JD" button: `btn-secondary` CSS class → inline `text-sky-700 bg-white border border-sky-200 rounded-xl hover:bg-sky-50`

### All Buttons
- **Before:** `btn-primary` / `btn-secondary` CSS classes
- **After:** Inline sky-to-green gradient — `bg-gradient-to-r from-sky-500 to-green-500 hover:from-sky-400 hover:to-green-400 text-white font-bold rounded-xl shadow-md shadow-sky-500/25 transition-all disabled:opacity-60 transform hover:-translate-y-0.5`
