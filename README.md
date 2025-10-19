# Face Recognition Door Lock System

> A real-time facial recognition system with liveness detection for access control. Features hot-reloading configuration and a simple web UI for real-time management.

## Demo So Far

[![Demo](https://img.youtube.com/vi/qjVI98kzM5E/0.jpg)](https://youtu.be/qjVI98kzM5E)

---

## Project Architecture

```
main.py (FastAPI entrypoint + lifespan management)
├── api/
│   ├── config.py         # Reading/writing config sections
│   ├── users.py          # CRUD for people + embedding ingestion
│   └── video.py          # Video control endpoints and MJPEG stream
├── runtime_services/
│   ├── state.py          # Long-lived runtime (video loop, mediapipe, orchestration)
│   └── embedding_manager.py  # Keeps DB changes synced with in-memory embeddings
├── face_recognition/
│   ├── face_recognizer.py  # InsightFace verification + scoring
│   ├── embeddings.py       # Helpers for vector math and caching
│   └── overlay.py          # OpenCV overlay renderer for HUD output
├── liveness/              # Eye-blink detection and liveness orchestration
├── notifications/
│   ├── notification_manager.py  # Routing + throttling for outbound alerts
│   ├── email.py / sms.py        # Individual providers
│   └── notification_util.py     # Shared helpers (tokens, templates, etc.)
├── database/
│   └── data_operations.py  # SQLite DAO with listener callbacks
├── config/
│   ├── config_manager.py  # Hot-reload config service + persistence
│   └── config.json        # Live runtime configuration
├── frontend/
│   ├── index.html
│   ├── scripts/           # config.js, users.js, video.js
│   └── styles/            # video.css and supporting stylesheets
├── utils/
│   ├── schemas.py         # Pydantic models used by API and config validation
│   └── enums.py           # Shared enums (access levels, config sections)
```

---

## Core Components

### Face Recognition
**Embeddings** — Generating normalized embeddings using InsightFace, and averaging multiple user images to create one unified embedding.

**Access levels** — Users at the door can either trigger a notification or trigger access control based on their relationship to system owner.

**In-memory cache** — `runtime_services.embedding_manager` acts as an in-memory store, allowing super fast lookup for cosine similarity.

### Configuration Management
**File-based configuration** — Using a JSON file for easy editing and persisted changes across page loads.

**Hot reloading** — Configuration changes applied without restarting the system.

**Listener callbacks** — `config_manager` pushes updates into the running `State` service so feature flags and thresholds take effect immediately.

### User Interface
**Simple HTML/CSS/JavaScript** — Lightweight with no complex frameworks.

**AJAX** — Real-time configuration updates through UI.

**User management** — Can add/remove users or their images and the backend takes care of the rest, including quickly recomputing average embeddings.

### Runtime & Video Pipeline
**FastAPI lifespan** — A shared `State` object is attached to the app for service coordination and clean shutdowns.

**Async and threading** — High compute operation run as a background task that cooperates with FastAPI through `asyncio`. This will however be changed to true multithreading when I upgrade the Python package to a free threaded build of Python.

**OpenCV overlay** — `Overlay` draws verification status, blink counts, and access decisions before frames stream to the UI.

**Liveness gate** — Blink detection uses the eye aspect ratio to avoid spoofing using MediaPipe's facial landmarks. Will add other liveness checks later.

### Notification System
**Modular design** — Easy to add new notification types using SOLID principles.

**Dynamic enabling/disabling** — Configuration UI allows quick changing of notification type. (Pending)

---

## Database Schema

> Data is persisted in SQLite and mirrored into memory by `runtime_services.embedding_manager` so recognition can run without blocking I/O. Tables are kept in sync via listener callbacks registered on the DAO.

#### **users**
```sql
id                INTEGER PRIMARY KEY
name              TEXT NOT NULL
access_level      TEXT NOT NULL
num_embeddings    INTEGER
embedding         BLOB  -- np.save format
```

#### **images**
```sql
img_name          TEXT
user_id           INTEGER NOT NULL
embedding         BLOB NOT NULL
PRIMARY KEY       (img_name, user_id)
```

---

## Technical Decisions

<table>
<tr>
<td width="50%">

### Why Enum for Notification Status?

**Mismatched return codes** — Twilio and Google use different error responses and codes, this unifies them, making them consistent for higher level modules.

**Self-documenting** — Clear, no magic numbers.

**Extensible** — Open-closed SOLID principle.

</td>
<td width="50%">

### Why SQLite over a vector DB?

**Lightweight** — No external database required, no installation, no configurations, and extremely portable.

**Fast** — SQLite is optimized for these small to medium sized datasets.

**Top K Search** — We only ever are interested in the top match. This means no grouped k nearest neighbor searches which is typically where a vector db shines. Because of this, the complexity of a vector db simply is not worth the benefits.

</td>
</tr>
<tr>
<td>

### Why MJPEG?

This is simply the most straightforward option. Again, the complexity of an HLS stream does not give enough benefit, and a WebRTC connection is not needed right now, though I could upgrade later to save on the bandwidth used by MJPEG.

</td>
<td>

### Why listener architectures?

**Decoupled reactions** — Services register callbacks instead of polling, so config, database, and runtime modules stay independent while still reacting instantly to changes.

**Hot reload friendly** — When `/config` updates land, listeners like `FaceRecognizer`, `Blink`, and `NotificationManager` receive only their section, avoiding full system restarts or global reloads.

**Consistent caches** — The embedding manager listens to database events so in-memory vectors update in lockstep with SQLite, keeping recognition accurate without extra queries.

</td>
</tr>
</table>

---

## Upcoming Steps

**ordered by priority**

- [ ] Program hardware (3D print clamp and mount for servo motor)
- [ ] Test basic end-to-end flow using computer
- [ ] Train a lightweight wake-word detection system so camera activates only when needed
- [ ] Add additional liveness checking (speech or IR when hardware allows)
- [ ] Update Python version and implement pure multithreading
- [ ] Add notifications and complete notification section

---

## Development Notes

> **Image Format Warning:** For user's images, be careful with jpegs. Depending on where you download them from they can be super lossy. I had much better success using pngs.
