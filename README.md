# Substations Telemetry Monitoring Dashboard

A Tkinter-based desktop application for monitoring power substations' telemetry data in real-time. Built for engineers to quickly identify operational issues across a fleet of devices.

## Video Walkthrough Link

[Watch Demo Video](https://youtu.be/...)  
*To be recorded after development completion*  
*Length: 2-3 minutes*  
*Shows: Fleet overview → Selected station → Voltage trend chart*

---

## Problem Definition

### The Challenge
Energy providers operate hundreds of power substations across vast geographic areas. Currently, the engineering team manually checks individual log files to monitor telemetry data (voltage, temperature, load) and identify failures. This approach is:

- **Time-consuming**: Takes 2+ hours daily to manually scan logs
- **Error-prone**: Easy to miss critical issues in hundreds of files
- **Not scalable**: Impossible to monitor all devices in real-time
- **Reactive**: Issues discovered only after problems occur

### Who Benefits
- **Operations Engineers**: Need rapid failure detection across their fleet
- **Maintenance Teams**: Want to anticipate equipment degradation before failures
- **Management**: Need visibility into fleet health and resource allocation

### What We're Solving
This dashboard provides:
1. **Centralized Fleet View**: See all substations at a glance, sorted by severity
2. **Real-time Status**: Color-coded health indicators (🟢 healthy, 🟡 warning, 🔴 critical)
3. **Drill-down Analytics**: Click any substation to see 24-hour voltage trends
4. **Smart Thresholds**: Automatic health classification based on configurable safety ranges

**Result**: Engineers can now identify and prioritize failures in minutes instead of hours.

---

## Setup & Deployment Instructions

### Prerequisites
- **Python 3.10+** installed
- Windows, macOS, or Linux
- No external dependencies (uses Python standard library only)

### Installation & Running

#### 1. Clone Repository
```bash
git clone <your-github-repo-url>
cd assessment
```

#### 2. Create Virtual Environment (Optional but Recommended)
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

#### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

*Note: No external dependencies required! requirements.txt is empty for Tkinter-only version.*

#### 4. Run Application
```bash
python main.py
```

The dashboard will launch in a new window showing:
- Fleet summary (healthy/warning/critical counts)
- Table of all 8 demo substations
- Station details on selection
- Voltage trend chart over last 24 hours

### Buttons

- **🔄 Refresh**: Re-evaluate all substations' health status
- **🔴 Reset**: Clear all data and regenerate fresh demo telemetry

### Demo Data

On launch, the app generates realistic telemetry for 8 demo substations:
- **SUB-001 to SUB-008** across various locations
- 24-hour history with realistic voltage/temperature/load patterns
- Pre-configured thresholds for health classification

---

## Technical Architecture

### Design Philosophy

**Separation of Concerns**: 
- `models.py` → Pure data (no imports from tkinter, service, or UI)
- `service.py` → Pure business logic (no tkinter, easy to test)
- `main.py` → UI only (depends on models + service)

This design makes it easy to:
- Swap UI framework (replace Tkinter with PyQt, PySimpleGUI, web, etc.)
- Add API endpoints (REST, GraphQL, WebSocket)
- Write comprehensive unit tests
- Reuse logic in different contexts

### Data Model

```
Thresholds (Configuration)
  ├─ voltage_min/max: Safety voltage range
  ├─ temperature_warn/crit: Temperature thresholds
  └─ load_warn/crit: Load thresholds

TelemetryReading (Immutable Historical Record)
  ├─ timestamp: When measurement was taken
  ├─ voltage: Voltage in volts
  ├─ temperature: Temperature in Celsius
  └─ load: Current load in amperes

SubstationState (Mutable Current Status)
  ├─ health: Current HealthStatus enum
  ├─ latest_reading: Most recent TelemetryReading
  └─ last_update: Timestamp of latest update

Substation (Complete Entity)
  ├─ station_id: Unique identifier
  ├─ location: Geographic location
  ├─ readings: List[TelemetryReading] (history)
  └─ state: SubstationState (current)

HealthStatus (Enum)
  ├─ HEALTHY: All metrics normal
  ├─ WARNING: One or more metrics approaching limit
  ├─ CRITICAL: One or more metrics exceeding limit
  └─ UNKNOWN: No data available
```

### Key Design Decisions

#### 1. Immutable TelemetryReading (frozen=True dataclass)
- **Why**: Historical data should never change
- **Benefit**: Prevents bugs from accidental mutations
- **Cost**: Cannot modify readings (create new ones instead)

#### 2. Separate SubstationState from History
- **Why**: Current status is mutable, history is immutable
- **Benefit**: Clear separation between "what happened" and "what's the current state"
- **Cost**: More classes to maintain

#### 3. Pure Functions in service.py
- **Why**: No hidden state, deterministic behavior
- **Benefit**: Easy to test, debug, and reason about
- **Cost**: Some functions have side effects (modifying Substation objects)

#### 4. Color Coding via Status Properties
- **Why**: UI doesn't need to know threshold values
- **Benefit**: Decouples UI from business logic
- **Cost**: Extra property method on SubstationState

### Module Responsibilities

**models.py** (≈150 lines)
- Define all data structures
- Validate data in __post_init__
- Provide helper methods (e.g., `get_readings_in_window()`)
- NO business logic, NO UI code

**service.py** (≈200 lines)
- Pure functions for health evaluation
- Telemetry ingestion logic
- Demo data generation
- Fleet statistics and queries
- NO UI code, NO database calls

**main.py** (≈350 lines)
- Tkinter UI components
- Event handlers
- Rendering charts
- Populating tables
- Calls service functions to get data

---

## Critical Reflection

### Decision: Computed Health vs. Stored Health Status

**What I Chose**: Compute health fresh each time from latest reading vs. threshold values (inside `evaluate_health()` function).

**Alternative Considered**: Store computed health in SubstationState, update only when new reading arrives.

### Trade-offs

| Aspect | Computed (Chosen) | Pre-computed |
|--------|-------------------|--------------|
| **Fresh Data** | Always reflects current data | Stale if thresholds change |
| **Performance** | Recalculation overhead | Fast lookup |
| **Flexibility** | Easy to change thresholds at runtime | Requires re-evaluation |
| **Complexity** | Simple (pure function) | More state management |
| **Testing** | Deterministic and easy | Must test state mutations |

### Why This Decision?

For this dashboard:
- Fleet is small (8 substations) → computation cost negligible
- Thresholds might need adjustment based on feedback → fresh computation needed
- Code clarity matters → pure function is easier to understand
- Testing matters → no state mutations to reason about

### When I'd Change It

If the system scaled to:
- **10,000+ substations** → Pre-compute and cache for performance
- **Real-time streaming data** → Event-driven updates (publish/subscribe pattern)
- **Historical "what-if" analysis** → Store multiple status snapshots over time

For this assessment MVP, computed status is the right choice.

---

## How to Extend This

### Add Real Log File Parsing
Replace `generate_demo_telemetry()` with file reader:
```python
def import_log_file(filepath: str, substation: Substation):
    # Parse CSV or JSON log file
    # Convert to TelemetryReading objects
    # Call ingest_reading() for each
```

### Add Database Persistence
Store readings in SQLite/PostgreSQL:
```python
def save_reading(reading: TelemetryReading):
    db.insert("telemetry_readings", {...})

def load_readings_since(station_id: str, since: datetime):
    return db.query("SELECT * WHERE station_id=? AND timestamp>=?")
```

### Add Alert Notifications
Send alerts when health transitions to CRITICAL:
```python
if old_health != HealthStatus.CRITICAL and new_health == HealthStatus.CRITICAL:
    send_email_alert(f"{substation.station_id} is CRITICAL!")
    send_sms_alert(f"{substation.location} needs attention")
```

### Add REST API
Expose dashboard data via API:
```python
# Use Flask to wrap service functions
@app.get("/api/substations")
def get_substations():
    return [serialize(s) for s in substations]

@app.get("/api/fleet/snapshot")
def get_fleet_status():
    return create_fleet_snapshot(substations).to_dict()
```

---

## Files Included

```
assessment/
├── models.py              # Data structures (dataclasses, enums)
├── service.py             # Business logic (pure functions)
├── main.py                # Tkinter UI application
├── requirements.txt       # Dependencies (empty for stdlib-only)
├── README.md              # This file
├── .gitignore
└── GIT_WORKFLOW.md        # Git branching strategy
```

---

## Testing

While this MVP doesn't include automated tests, the design makes testing easy:

```python
# Test health evaluation (pure function)
reading = TelemetryReading(
    timestamp=now,
    voltage=260.5,  # Above max of 260
    temperature=50.0,
    load=30.0,
)
assert evaluate_health(reading, thresholds) == HealthStatus.CRITICAL

# Test state update
sub = Substation("SUB-001", "Location")
ingest_reading(sub, reading, thresholds)
assert sub.state.health == HealthStatus.CRITICAL
```

All business logic in `service.py` can be tested without UI dependencies.

---

## Author Notes

This dashboard demonstrates:
- ✅ Clean separation of concerns (models, service, UI)
- ✅ Type-safe data structures (dataclasses with validation)
- ✅ Testable business logic (pure functions)
- ✅ User-friendly interface (color coding, drill-down)
- ✅ Scalable architecture (easy to add features)

Built with Python standard library only (Tkinter) to show focus on fundamentals.

---

## License

Open source for assessment purposes.
#   A s s e s s m e n t 1  
 