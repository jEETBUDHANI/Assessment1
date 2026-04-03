# Energy Telemetry Monitoring MVP - Assessment Plan

## 1. HIGH-VALUE MVP FEATURE PRIORITIZATION

### Core Problem
Engineering teams manually inspect log files—this is **slow**, **error-prone**, and doesn't scale across hundreds of substations.

### MVP Feature Set (Prioritized by Value)
**Tier 1 (Must-Have for Demo):**
1. **Real-time Alert Dashboard** ← Start here
   - Displays active failures/anomalies across all substations
   - Color-coded status (OK/WARNING/CRITICAL)
   - Quick visual scan shows immediate problems
   - *User Value*: Replaces manual log checking; answers "What's broken right now?"

2. **Substation Status Grid/List**
   - Shows all substations with latest metrics (voltage, load, temp)
   - Click to drill down into device details
   - *User Value*: Centralized overview replaces checking 100+ separate log files

3. **Time-series Data View**
   - Graph showing voltage/temp/load trends over last 24 hours for selected substation
   - *User Value*: Identify patterns and degradation before failures

**Tier 2 (Nice-to-Have, skip if time-constrained):**
- Historical data export
- Failure prediction patterns
- Multi-device comparison

### Why This MVP Works
- **Immediate user value**: Eliminates manual log inspection
- **Technically achievable in 4 hours**: Built-in Python plotting (matplotlib) + simple data model
- **Demo-friendly**: Shows visual results quickly
- **Extensible**: Easy to add features in Tier 2

---

## 2. CLEAN DATA MODEL FOR SUBSTATIONS & TELEMETRY

### Data Model Design Philosophy
- **Immutable telemetry records**: All sensor readings are historical facts
- **Mutable device status**: Track current state for alerts
- **Separation of concerns**: Raw data vs. computed state

### Core Data Structure (Python 3.10+ Dataclasses)

```python
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import List, Optional

class DeviceStatus(Enum):
    """Status classification for devices"""
    OK = "ok"
    WARNING = "warning"
    CRITICAL = "critical"

@dataclass
class TelemetryReading:
    """Single sensor reading - immutable historical record"""
    timestamp: datetime
    voltage: float  # volts
    current_load: float  # amperes
    temperature: float  # celsius
    
    def __post_init__(self):
        """Validate reading constraints"""
        if not (0 <= self.voltage <= 1000):
            raise ValueError(f"Invalid voltage: {self.voltage}")
        if not (0 <= self.temperature <= 100):
            raise ValueError(f"Invalid temperature: {self.temperature}")

@dataclass
class Substation:
    """Represents a single power substation"""
    station_id: str  # e.g., "SUB-001"
    location: str  # e.g., "North District"
    readings: List[TelemetryReading] = field(default_factory=list)
    
    @property
    def latest_reading(self) -> Optional[TelemetryReading]:
        """Get most recent telemetry"""
        return self.readings[-1] if self.readings else None
    
    @property
    def status(self) -> DeviceStatus:
        """Compute current status based on latest reading"""
        if not self.latest_reading:
            return DeviceStatus.WARNING
        
        reading = self.latest_reading
        # Rules for critical/warning thresholds
        if reading.temperature > 85 or reading.voltage > 950:
            return DeviceStatus.CRITICAL
        elif reading.temperature > 75 or reading.voltage > 900:
            return DeviceStatus.WARNING
        return DeviceStatus.OK
    
    def add_reading(self, reading: TelemetryReading) -> None:
        """Append new telemetry reading"""
        self.readings.append(reading)
    
    def get_readings_since(self, since: datetime) -> List[TelemetryReading]:
        """Filter readings after timestamp (for time-series charts)"""
        return [r for r in self.readings if r.timestamp >= since]

@dataclass
class Facility:
    """Collection of all monitored substations"""
    substations: List[Substation] = field(default_factory=list)
    
    def add_substation(self, substation: Substation) -> None:
        self.substations.append(substation)
    
    def get_critical_stations(self) -> List[Substation]:
        """Alert dashboard: Show failures first"""
        return [s for s in self.substations 
                if s.status == DeviceStatus.CRITICAL]
    
    def get_warning_stations(self) -> List[Substation]:
        """Alert dashboard: Show warnings"""
        return [s for s in self.substations 
                if s.status == DeviceStatus.WARNING]
```

### Why This Model Works
| Aspect | Why |
|--------|-----|
| **Immutable TelemetryReading** | Historical data never changes; prevents bugs from accidental mutations |
| **@property for status** | Computed on-demand; no stale state to manage |
| **Separate Facility class** | Represents the full system; easier to test and extend |
| **Type hints** | Clean, self-documenting; easier for team review |
| **Validation in __post_init__** | Catches bad sensor data early |

---

## 3. RECOMMENDED PROJECT STRUCTURE

```
assessment/
├── README.md                    # Required sections (see below)
├── requirements.txt             # Dependencies (PyQt5, matplotlib, pandas)
├── .gitignore
├── data/
│   ├── sample_telemetry.json   # Test data
│   └── (generated outputs)
├── src/
│   ├── __init__.py
│   ├── models.py               # Data model (dataclasses above)
│   ├── data_loader.py          # Parse log files → TelemetryReading
│   ├── ui/
│   │   ├── __init__.py
│   │   ├── main_window.py      # PyQt5 main window
│   │   ├── dashboard.py        # Alert dashboard widget
│   │   └── detail_view.py      # Drill-down detail view
│   └── utils/
│       ├── validators.py       # Input validation
│       └── time_helpers.py     # Datetime utilities
├── tests/
│   ├── test_models.py          # Unit tests for data model
│   ├── test_data_loader.py     # Test log parsing
│   └── test_ui.py              # Basic UI tests
├── docs/
│   ├── ARCHITECTURE.md         # Technical deep dive
│   └── DESIGN_DECISIONS.md     # Trade-offs & alternatives
└── main.py                      # Entry point
```

---

## 4. GIT WORKFLOW (STRICT BRANCHING)

### Workflow Steps

**Step 1: Initialize Repository**
```bash
git init
git add .
git commit -m "chore: initial project structure"
git branch -M main
```

**Step 2: Create Feature Branch** (for each feature)
```bash
git checkout -b feature/alert-dashboard
# Make changes...
git add .
git commit -m "feat: implement real-time alert dashboard widget"
git push origin feature/alert-dashboard
# Create Pull Request (via GitHub UI)
# After review/approval: Merge into main
git checkout main
git merge --ff-only feature/alert-dashboard
```

**Step 3: Commit Message Convention**
```
<type>: <description>

<optional body explaining why>
```

**Types:**
- `feat:` - New feature
- `fix:` - Bug fix
- `refactor:` - Code restructuring (no behavior change)
- `test:` - Add/update tests
- `docs:` - Documentation
- `chore:` - Config, dependencies, etc.

**Examples:**
```
feat: add telemetry data model with validation
fix: handle missing timestamp in log parsing
test: add unit tests for DeviceStatus computation
docs: add setup instructions to README
refactor: extract status calculation logic
```

### Branch Strategy
- Always branch FROM `main`
- One feature per branch
- PR required before merge
- Delete merged branches

---

## 5. TIMELINE: 4 HOURS ACTIVE WORK

| Phase | Time | Tasks |
|-------|------|-------|
| **Setup** | 20 min | Git init, create branches, install PyQt5 |
| **Core Model** | 40 min | Implement dataclasses + sample data generation |
| **Data Loading** | 30 min | Parse simple JSON/CSV log format into model |
| **UI - Dashboard** | 90 min | PyQt5 table showing status; color coding |
| **UI - Detail View** | 40 min | Matplotlib chart for single substation trends |
| **Testing + Polish** | 20 min | Run unit tests, ensure app launches cleanly |

**Total: ~4.5 hours** (adjust scope if needed)

---

## 6. REQUIRED README.md SECTIONS

```markdown
# Energy Telemetry Monitoring System

## 1. Video Walkthrough Link
[Watch Demo (2:30)](https://youtu.be/...)
- Shows alert dashboard loading
- Drills down into a failing substation
- Displays 24-hour trend chart

## 2. Problem Definition
**User Need:** Engineering teams waste 2+ hours daily manually checking log files across 300+ substations to find failures.

**Key Pain Points:**
- No centralized view of all devices
- Delays in spotting critical issues
- No historical trend visibility

**Solution:** Desktop dashboard showing real-time status + drill-down trends.

## 3. Setup & Deployment

### Prerequisites
- Python 3.10+
- Windows/Mac/Linux

### Local Setup
\`\`\`bash
git clone <repo>
cd assessment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
python main.py
\`\`\`

### Load Sample Data
App loads sample_telemetry.json automatically on startup.

## 4. Technical Architecture

### Data Model
- **TelemetryReading**: Immutable sensor readings (voltage, load, temp, timestamp)
- **Substation**: Container with readings list + computed status property
- **Facility**: Collection of substations; provides query methods for alerts

See [src/models.py](src/models.py) for details.

### Logic Separation
- **models.py**: No UI dependencies; pure data + business logic
- **data_loader.py**: Parses external formats
- **ui/**: PyQt5 widgets; observes model state

### Why This Design
✓ Easy to test (models don't import PyQt5)
✓ Easy to swap UI framework later
✓ Reusable data layer for APIs/CLI

## 5. Critical Reflection

### Decision: Computed Status vs. Stored State
**What I chose:** `status` as `@property` (computed on-demand)

**Pros:**
- No stale state; always reflects current data
- Single source of truth (latest reading)

**Cons:**
- Recalculates on every access (minor performance hit)
- Can't track status *history* without logging

**Trade-off:** For this MVP with ~500 readings, recalculation is negligible. 
If we scale to millions of readings, I'd consider:
- Caching status with timestamp
- Event-driven updates (publish status changes)
- Time-series database for historical state

**Would I change it?** Not for this assessment; the simple approach is more maintainable.
```

---

## 7. SAMPLE IMPLEMENTATION CHECKLIST

- [ ] **Phase 1:** Create GitHub repo + set up branches
- [ ] **Phase 2:** Implement data model (dataclasses)
- [ ] **Phase 3:** Create sample_telemetry.json (5 substations, 20 readings each)
- [ ] **Phase 4:** Write data_loader.py to parse JSON
- [ ] **Phase 5:** Implement main PyQt5 window
- [ ] **Phase 6:** Build alert dashboard (status grid, color coding)
- [ ] **Phase 7:** Build detail view (matplotlib chart)
- [ ] **Phase 8:** Write unit tests for models + data loader
- [ ] **Phase 9:** Test end-to-end (run main.py, verify UI)
- [ ] **Phase 10:** Record 2-3 min video walkthrough
- [ ] **Phase 11:** Update README with all 5 sections
- [ ] **Phase 12:** Final commit + push to main

---

## 8. KEY DECISION: MVP SCOPE

**Keep it simple:**
- DO: Dashboard + drill-down + chart
- DON'T: Real log file parsing, database, authentication, cloud sync

**Why?** 4 hours isn't enough. Show clean code + working features + thoughtful architecture. Interviewers care more about *how you think* than *how much you build*.

---

## NEXT STEPS

1. Create GitHub repository
2. Use this structure to create your branches
3. Start with Phase 1-2 (setup + data model design review)
4. Proceed through checklist methodically
5. Record walkthrough after Phase 7

Good luck! This assessment prioritizes showing solid fundamentals over feature completeness.
