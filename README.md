# parking
Collaborative Parking App
Got it — let’s stitch everything together into a **single coherent README** with a concise intro at the top.
I’ll keep the intro short and sober: what the project is, what the PoC does, and why it exists.

---

# 🅿️ Collaborative Parking App (PoC)

## 📌 Project Overview

A **privacy-safe, crowdsourced parking app**.
Users report when they **leave** or **find** a parking spot. Others see the spot on a map as an **approximate fuzzy circle** (not exact GPS).
Spots **expire dynamically** (shorter in busy zones, longer in quieter ones).
Goal of this PoC: **prove the core loop** before investing in gamification, ML, or monetization.

---

## 🎯 PoC Goal

> *User reports a spot → Others see obfuscated marker nearby → Marker decays dynamically based on context.*

---

## 1. Backend (FastAPI + Postgres/PostGIS)

### Core API Endpoints

* **POST /spot** → Report leaving/found spot. Backend snaps GPS to a cell (\~100 m), delays publishing (anti-tracking), sets dynamic TTL (3–10 min).
* **GET /spots** → Return nearby spots as cell centroids + TTL countdown + confidence label.

### DB Schema

```sql
CREATE TABLE parking_spots (
    id SERIAL PRIMARY KEY,
    user_id TEXT,
    type VARCHAR(10) CHECK (type IN ('leaving', 'found')),
    location GEOGRAPHY(POINT, 4326), -- raw GPS, internal use
    cell_id TEXT,                    -- obfuscated cell
    created_at TIMESTAMP DEFAULT NOW(),
    expires_at TIMESTAMP,
    confidence VARCHAR(10)           -- "high", "medium", "low"
);
```

---

## 2. Frontend (Android App via Expo)

### Minimal UI

* **Map Screen** → fuzzy circles (\~100 m radius) instead of exact pins; fading opacity as TTL decreases.
* **Report Screen** → two buttons: 🚗 *Leaving Spot* and 🅿️ *Found Empty Spot*.

### Data Flow

1. User reports → backend stores raw GPS, snaps to cell, adds TTL + delay.
2. Others fetch → see obfuscated circle + “Fresh/Fading/Likely gone”.
3. Spots disappear when expired.

---

## 3. Privacy by Design

* No raw GPS exposed to clients (only obfuscated cells).
* “Leaving” signals published after **movement >100 m or 60–90 s delay**.
* No identity shown; optional photos deferred.
* TTL adaptive → reduces stale data & false hope.

---

## 4. Deployment (PoC-friendly, free tiers)

* **API Host:** Render Free Web Service (FastAPI container).
* **Database:** Supabase Free Postgres + PostGIS (with free object storage).
* **Cache (optional later):** Upstash Redis Free (256 MB, 500K ops/mo).
* **Alternative DB:** Neon Postgres (also supports PostGIS).
* **Why not EC2?** Free tier (t2.micro) exists but requires more ops & config.

---

## 5. Mobile Setup

* **Stack:** React Native + Expo (develop in VS Code, test on Android phone with Expo Go).
* **Map library:** MapLibre RN (open-source tiles).
* **Release builds:** Expo’s EAS Build → Play Store later.

---

## 6. Config (env-style for tuning)

* `CELL_SIZE_METERS=100`
* `PUBLISH_DELAY_SECONDS=75`
* `TTL_BAND=CBD_PEAK:180|URBAN:360|RESIDENTIAL:600`
* `OBFUSCATION_JITTER_METERS=15`
* `CONFIDENCE_THRESHOLDS=FRESH:<90s|FADING:<240s|LOW:>=240s`

---

## 7. Pilot Testing Plan

* Deploy backend + app; recruit \~20–30 testers.
* Collect metrics:

  * Avg. spot lifetime.
  * % spots still free when checked.
  * Tester feedback on fuzzy circles.
* Use data to refine TTL bands → survival curve–based predictions later.

---

## 8. Roadmap (after PoC)

* Add **user reputation** weighting.
* Allow **photo evidence** (blurred plates/faces).
* Analytics dashboard (spot turnover, accuracy).
* ML-based TTL instead of rules.
* Gamification + freemium tier.

---

👉 This README gives you a **self-contained blueprint**: what the project is, what the PoC does, how to deploy it free, and what’s next.

---

Would you like me to now add the **folder structure + docker-compose sketch** into this README (so you can literally spin it up locally), or keep that separate?
