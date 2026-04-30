# VideoInterview.jsx — Theme Changes

## Summary
Full sky/green light theme applied to every part of the interview UI — page background, header, persona card, webcam view, transcript panel, control bar, and ThankYouScreen. All dark slate colors replaced with the sky/green palette.

## Changes Made

### Main Page Background
- **Before:** `bg-slate-950` / `bg-gradient-to-br from-sky-950 via-slate-900 to-sky-950`
- **After:** `bg-gradient-to-br from-sky-50 via-white to-green-50 font-sans` with fixed ambient glow blobs (sky left, green right)

### Header (Top Bar)
- **Before:** `bg-slate-900/80 border-slate-800/60` (dark)
- **After:** `bg-white/80 border-sky-200 backdrop-blur-sm shadow-sm`
- Brand icon: `Shield bg-brand-600` → `Leaf` in `from-sky-600 to-green-600` gradient (matching Login.jsx navbar)
- Page title: `text-white` → `text-sky-950 font-bold`
- Round label: `text-slate-500` → `text-sky-500`
- LIVE badge: `bg-red-500/15 border-red-500/30 text-red-400` → `bg-red-50 border-red-200 text-red-500`
- Timer: `text-slate-500` → `text-sky-500 font-medium`
- Turn counter: plain text → `bg-sky-50 border-sky-200 text-sky-400 rounded-full px-2`

### PersonaCard
- **Before:** `bg-slate-900/80 border-slate-700/50` (dark container)
- **After:** `bg-white/90 backdrop-blur-sm border border-sky-200/80 shadow-lg shadow-sky-900/10`
- Gradient wash: `opacity-[0.06]` (kept, subtle on light bg)
- Persona name: `text-white` → `text-sky-950 font-bold`
- Persona sub-text: `text-slate-400` / `text-sky-400` → `text-sky-500`
- Status badge backgrounds: dark `bg-{color}-500/15 border-{color}-400/30 text-{color}-300` → light `bg-{color}-50 border-{color}-200 text-{color}-600`
- StatusDot idle: `bg-slate-400/60` / `bg-sky-400/60` → `bg-sky-300`
- Processing spinner: `text-amber-400` → `text-amber-500`
- Last reply bubble: `bg-sky-900/70 border-sky-700/40 text-sky-100` → `bg-sky-50 border-sky-200 text-sky-800 shadow-sm`
- Speaking wave: `color: rgba(255,255,255,0.8)` → `text-sky-500`
- Ring opacity values slightly reduced for visibility on light background

### CandidateView (Webcam)
- **Before:** `bg-sky-900/60 border-sky-800/50` (dark)
- **After:** `bg-sky-50 border-sky-200 shadow-md shadow-sky-900/10`
- Camera error text: `text-sky-500` (unchanged)
- Proctoring badge: `bg-black/60 border-red-500/30 text-red-400` → `bg-white/80 border-red-200 text-red-500 shadow-sm`
- Name badge: `bg-black/50 text-white` → `bg-white/80 border-sky-200 text-sky-900 font-semibold shadow-sm`

### Transcript Panel
- **Before:** `bg-sky-950/60 border-sky-800/60` (dark)
- **After:** `bg-white/90 backdrop-blur-sm border border-sky-200/80 shadow-lg shadow-sky-900/10`
- Label: `text-sky-500/70` → `text-sky-400 font-bold`
- Placeholder text: `text-sky-600` → `text-sky-400 italic`
- Speaker labels: `text-sky-500/70` → `text-sky-400 font-bold`
- Your message bubble: `text-sky-100 bg-sky-600/25 border-sky-500/20` → `text-sky-900 bg-sky-100 border-sky-200`
- Persona reply bubble: `text-sky-200 bg-sky-900/70 border-sky-700/30` → `text-sky-800 bg-sky-50 border-sky-200`

### TypingIndicator
- **Before:** `bg-sky-900/70 border-sky-700/30` (dark)
- **After:** `bg-sky-50 border-sky-200`
- Label: `text-sky-500/70` → `text-sky-400`
- Dots: `bg-sky-400` (unchanged)

### TalkButton
- Disabled: `bg-sky-900` → `bg-sky-100`
- Active (not recording): `bg-gradient-to-r from-sky-500 to-green-500` with `shadow-sky-500/35` (same gradient, no change)
- Focus ring: `focus-visible:ring-sky-400/50` (unchanged)
- Label: `text-sky-500` (unchanged)

### Control Bar (Footer)
- **Before:** `bg-sky-950/80 border-sky-800/60` (dark)
- **After:** `bg-white/80 border-sky-200 backdrop-blur-sm` with subtle upward sky shadow
- Error banner: `bg-red-500/10 border-red-500/30 text-red-400` → `bg-red-50 border-red-200 text-red-600 font-medium`
- Leave button container: `bg-sky-900 hover:bg-sky-800` → `bg-sky-100 hover:bg-sky-200`
- Leave button color: `text-sky-600 hover:text-sky-400` → `text-sky-500 hover:text-sky-700`
- Start Interview button: `bg-emerald-600 hover:bg-emerald-700 shadow-emerald-500/30` → `bg-emerald-500 hover:bg-emerald-600 shadow-emerald-400/30` with hover lift
- Start Interview label: `text-sky-500` (unchanged)
- Volume icon (idle): `bg-sky-900 text-sky-600` → `bg-sky-100 text-sky-400`
- Volume icon (speaking): `bg-emerald-500/20 text-emerald-400` → `bg-emerald-100 text-emerald-600`
- "Audio" label: `text-sky-600` → `text-sky-400 font-medium`
- Instruction hint: `text-sky-600` → `text-sky-400 font-medium`

### ThankYouScreen
- Background: `bg-slate-950` (dark) → `bg-gradient-to-br from-sky-50 via-white to-green-50` with ambient glows
- Heading: `text-white` → `text-sky-950 font-extrabold tracking-tight`
- Sub-text: `text-slate-400 / text-white` → `text-sky-700 / text-sky-950 font-bold`
- "What's next" box: `bg-slate-800/60 border-slate-700/50` → `bg-white/90 backdrop-blur-sm border-sky-200 shadow-lg`
- Section title: `text-slate-300` → `text-sky-800 font-bold`
- List items: `text-slate-400` → `text-sky-700`
- Return button: `btn-primary` CSS class → inline sky-to-green gradient button
