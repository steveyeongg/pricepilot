# PricePilot 🛩️

> **Know the right price — instantly, automatically and with confidence.**
> 
> *Your smart pricing co-pilot!*

A Dynamic Pricing & Competitor Intelligence Platform for Malaysian markets. Track prices across Lazada, Shopee, Temu, and major grocery retailers. Get fair price analytics, smart alerts, and ROI optimization — all in one place.

---

## Features

| Feature | Free Tier | Pro |
|---|---|---|
| Competitor price tracking | ✅ | ✅ |
| Fair price intelligence | ✅ | ✅ |
| Automated monitoring | — | ✅ |
| Pricing insights dashboard | — | ✅ |
| Smart alerts | — | ✅ |
| ROI & profit optimization | — | ✅ |

## Platforms Covered

**E-commerce:** Lazada, Shopee, Temu, Amazon, Alibaba  
**Grocery:** Jaya Grocer, Village Grocer, Lotus, AEON, AEON Big  
**Electronics:** Various gadget stores

---

## Quick Start

### Prerequisites
- Python 3.11+
- Node.js 18+
- PostgreSQL (or use Supabase free tier)

### 1. Clone & configure

```bash
git clone <repo>
cd PricePilot
cp .env.example .env
# Edit .env with your credentials
```

### 2. Backend

```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

### 3. Frontend (Next.js App)

```bash
cd frontend
npm install
npm run dev
# Open http://localhost:3000
```

---

## Free Hosting Stack

| Service | Platform | Sign Up |
|---|---|---|
| Frontend | [Vercel](https://vercel.com) | Free |
| Backend | [Render](https://render.com) | Free (750 hrs/mo) |
| PostgreSQL | [Supabase](https://supabase.com) | 500MB free |
| Redis cache | [Upstash](https://upstash.com) | 10k req/day free |
| HTML page | [GitHub Pages](https://pages.github.com) | Free |

---

## API Docs

Once running, visit `http://localhost:8000/docs` for interactive Swagger UI.

Key endpoints:
- `GET /api/search?q=iphone&platforms=lazada,shopee` — cross-platform search
- `POST /api/products` — add product to track
- `GET /api/products/{id}/analytics` — fair price + market analysis
- `POST /api/roi/simulate` — ROI simulation
- `POST /api/alerts` — create price alert

---

## Project Vision

*"Know the right price — instantly, automatically and with confidence."*

Built for Malaysian SMEs, online sellers, and price-conscious consumers who deserve data-driven pricing intelligence without enterprise-grade costs.
