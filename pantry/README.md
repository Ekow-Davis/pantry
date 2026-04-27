# pantry (MealWise Frontend)

Vue 3 + Vite + TypeScript PWA frontend for **MealWise** — a personal meal planner focused on Ghanaian and West African cuisine.

---

## Tech Stack

| Layer | Choice |
|---|---|
| Framework | Vue 3 (Composition API + `<script setup>`) |
| Build tool | Vite 8 |
| Language | TypeScript |
| Styling | Tailwind CSS v4 (via `@tailwindcss/vite`) |
| State | Pinia |
| Routing | Vue Router 4 |
| HTTP | Axios with JWT interceptors |
| Icons | Lucide Vue Next |
| PWA | vite-plugin-pwa (Workbox) |
| Fonts | Playfair Display (display) + Plus Jakarta Sans (body) |
| Deployment | Vercel |

---

## Project Structure

```
src/
├── assets/
├── components/
│   ├── general/
│   │   ├── ToastContainer.vue    # Global toast notifications
│   │   ├── ThemeSwitcher.vue     # Dark/light + accent colour picker
│   │   └── PageLoader.vue        # Full-screen loading overlay
│   └── layout/
│       ├── HomeLayout.vue        # Public nav + footer
│       ├── AuthLayout.vue        # Centred auth wrapper
│       ├── AppLayout.vue         # Sidebar (desktop) + bottom nav (mobile)
│       └── AdminLayout.vue       # Admin sidebar + header
├── composables/
│   ├── useTheme.ts               # Theme mode + accent colour logic
│   └── useApi.ts                 # Axios instance with JWT + refresh
├── pages/
│   ├── Home/                     # Landing, HowItWorks, About, Contact, Donate
│   ├── Auth/                     # Login, Register, ForgotPassword, ResetPassword
│   ├── App/                      # Dashboard, Plan, Meals, MealDetail, Pantry,
│   │                             # History, Contribute, Settings
│   ├── Admin/                    # Dashboard, Users, Meals, Contributions,
│   │                             # Ingredients, Stats
│   └── General/
│       └── NotFoundPage.vue
├── router/
│   └── index.ts                  # All routes + navigation guards
├── stores/
│   ├── auth.ts                   # Token, user, login, logout
│   ├── ui.ts                     # Sidebar + mobile nav state
│   ├── notifications.ts          # Toast queue
│   ├── meals.ts                  # Meal library + meal of the day
│   ├── plan.ts                   # Daily plan + slot management
│   └── admin.ts                  # Admin data
├── utils/
│   └── format.ts                 # Date/string helpers
├── style.css                     # Design tokens + utilities + animations
└── main.ts
```

---

## Local Setup

### 1. Install dependencies

```bash
npm install
```

### 2. Configure environment

Create a `.env` file in the project root:

```env
VITE_API_URL=http://localhost:8000
```

### 3. Start dev server

```bash
npm run dev
```

The app runs at `http://localhost:5173`.

### 4. Build for production

```bash
npm run build
```

---

## Theme System

The app supports **light/dark mode** and **5 accent colour presets**, persisted to `localStorage`.

| Setting | localStorage key | Options |
|---|---|---|
| Mode | `mw-theme` | `light`, `dark` |
| Accent | `mw-accent` | `chili`, `orange`, `turmeric`, `amber`, `cocoa` |

Theme is applied via `data-theme` and `data-accent` attributes on `<html>`. CSS custom properties update everything instantly — no page reload needed.

Users adjust both settings from the **Settings** page or the **ThemeSwitcher** in the navbar.

---

## PWA

This is a Progressive Web App. On mobile, users can install it via "Add to Home Screen" — no app store required.

- Place `icon-192.png` and `icon-512.png` in the `public/` folder before building.
- Service worker caching: meal library uses `StaleWhileRevalidate`, daily plan uses `NetworkFirst`.

---

## Routes Summary

| Path | Access | Description |
|---|---|---|
| `/` | Public | Landing page |
| `/how-it-works` | Public | Feature walkthrough |
| `/about` | Public | About the project |
| `/contact` | Public | Contact form |
| `/donate` | Public | Support the project |
| `/auth/login` | Guest only | Sign in |
| `/auth/register` | Guest only | Create account |
| `/app/dashboard` | Auth | Dashboard |
| `/app/plan` | Auth | Today's meal plan |
| `/app/meals` | Auth | Meal library |
| `/app/meals/:id` | Auth | Meal detail + recipe |
| `/app/pantry` | Auth | What can I cook? |
| `/app/history` | Auth | Meal log history |
| `/app/contribute` | Auth | Submit a recipe |
| `/app/settings` | Auth | Theme + preferences |
| `/admin/*` | Admin only | Admin panel |

---

## Deployment (Vercel)

The `vercel.json` handles SPA routing. Set `VITE_API_URL` in Vercel's environment variables to point at your production backend on Railway.

---

## 3D Assets and Animation Recommendations

For richer visuals beyond CSS animations, these free resources work well:

| Type | Source | Notes |
|---|---|---|
| Lottie animations | [LottieFiles](https://lottiefiles.com) — search "cooking", "bowl", "meal" | Use `@lottiefiles/vue-lottie-player` |
| Spline 3D scenes | [Spline](https://spline.design) | Export as embed or use `@splinetool/vue-spline` |
| 3D food models | [Sketchfab](https://sketchfab.com) — search "jollof", "fufu", "plantain" | Filter by free licence (.glb/.gltf) |
| Three.js | [Three.js](https://threejs.org) + `three` npm package | Full 3D if you want it |

For the hero section specifically, a Spline scene of a rotating food bowl or a Lottie cooking loop would match the animation style from your reference video — warm colours, looping, not too heavy.
