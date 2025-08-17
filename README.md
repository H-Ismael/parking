
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

### Core Endpoints

#### **POST /spot** → report leaving/found spot

**Request payload:**

```json
{
  "user_id": "hashed_or_uuid",
  "lat": 34.020882,
  "lon": -6.841650,
  "type": "leaving",   // or "found"
  "timestamp": "2025-08-16T14:00:00Z"
}
```

**Backend logic:**

* Store raw GPS (internal use).
* Snap to cell (\~100 m).
* Apply **publish delay** (anti-tracking).
* Compute `expires_at` based on TTL rules (zone/time).

**Response example:**

```json
{
  "status": "ok",
  "spot_id": 123,
  "cell_id": "cell_34.021_-6.842",
  "expires_at": "2025-08-16T14:05:00Z"
}
```

---

#### **GET /spots** → fetch available spots

**Query params:**

* `lat` (float) → user location
* `lon` (float) → user location
* `radius_meters` (int, optional, default=1000)

**Response example:**

```json
{
  "spots": [
    {
      "id": 123,
      "cell_lat": 34.021,        // centroid of obfuscated cell
      "cell_lon": -6.842,
      "type": "found",
      "expires_in": 180,         // seconds remaining
      "confidence": "medium"     // "high", "medium", "low"
    },
    {
      "id": 124,
      "cell_lat": 34.019,
      "cell_lon": -6.840,
      "type": "leaving",
      "expires_in": 300,
      "confidence": "high"
    }
  ]
}
```

---

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
