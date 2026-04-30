# Login.jsx — Theme Changes

## Summary
The Login page is the design reference for the application's sky/green theme. The changes below were applied to establish this baseline and improve icon visibility.

## Changes Made

### Leaf Icon — Navbar
- **Background gradient** darkened from `from-sky-500 to-green-500` → `from-sky-600 to-green-600`
- **Shadow** strengthened: `shadow-sky-500/30` → `shadow-sky-600/50`
- **Ring outline** added: `ring-2 ring-sky-400/40` for extra definition against light backgrounds
- **Icon** gained `drop-shadow-sm` to lift it off the container

### Leaf Icon — Login Modal Left Panel
- **Container opacity** raised from `bg-white/20` → `bg-white/40` so it stands out against the gradient panel
- **Border opacity** raised from `border-white/30` → `border-white/50`
- **Shadow** added: `shadow-lg shadow-sky-900/20`
- **Icon** gained `drop-shadow` utility

## Design Tokens Established (used across all pages)

| Token | Value |
|-------|-------|
| Background | `bg-gradient-to-br from-sky-50 via-white to-green-50` |
| Card | `bg-white/90 backdrop-blur-sm rounded-2xl border border-sky-200/80 shadow-lg shadow-sky-900/10` |
| Primary button | `bg-gradient-to-r from-sky-500 to-green-500 hover:from-sky-400 hover:to-green-400 text-white font-bold rounded-xl shadow-md shadow-sky-500/25` |
| Input | `bg-gray-50 border border-gray-200 focus:ring-2 focus:ring-sky-500 focus:border-sky-500 rounded-xl` |
| Heading | `text-sky-950` (h1) / `text-sky-900` (h2) |
| Body text | `text-sky-700/70` |
| Ambient glow left | `bg-sky-300/15 blur-[100px]` |
| Ambient glow right | `bg-green-300/10 blur-[120px]` |
