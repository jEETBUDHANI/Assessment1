# 📖 File Directory Reference

Quick reference for all files in your assessment package.

---

## 🎯 Submission Files (Required)

```
README.md
├─ ✅ Video Walkthrough Link
├─ ✅ Problem Definition
├─ ✅ Setup & Deployment
├─ ✅ Technical Architecture
└─ ✅ Critical Reflection
```

**This is what you submit to GitHub!**

---

## ⚙️ Application Files (Core)

### models.py (~180 lines)
**Purpose:** Data structures with no UI dependencies

**Contains:**
```
HealthStatus (Enum)
  ├─ HEALTHY, WARNING, CRITICAL, UNKNOWN

Thresholds (Dataclass)
  ├─ voltage_min/max, voltage_warn
  ├─ temperature_warn/crit
  └─ load_warn/crit

TelemetryReading (Dataclass, Frozen)
  ├─ timestamp (datetime)
  ├─ voltage (float)
  ├─ temperature (float)
  └─ load (float)

SubstationState (Dataclass)
  ├─ station_id, location
  ├─ health: HealthStatus
  ├─ latest_reading: TelemetryReading
  └─ get_status_color() → str

Substation (Dataclass)
  ├─ station_id, location
  ├─ readings: List[TelemetryReading]
  ├─ state: SubstationState
  ├─ get_readings_in_window(hours) 
  └─ add_reading()

FleetSnapshot (Dataclass)
  ├─ total_substations, healthy_count
  ├─ warning_count, critical_count
  ├─ unknown_count
  └─ healthy_percentage, issues_count (properties)
```

**How to use:**
```python
from models import TelemetryReading, Substation, HealthStatus

reading = TelemetryReading(
    timestamp=datetime.now(),
    voltage=230.5,
    temperature=45.0,
    load=50.0
)

sub = Substation("SUB-001", "North District")
sub.add_reading(reading)
```

---

### service.py (~220 lines)
**Purpose:** Business logic (pure functions, testable)

**Contains:**
```
evaluate_health()
  → Takes reading + thresholds
  → Returns HealthStatus

ingest_reading()
  → Adds reading to substation
  → Updates state
  → Returns health

create_fleet_snapshot()
  → Analyzes all substations
  → Returns aggregated stats

count_health_statuses()
  → Counts by status
  → Returns (healthy, warning, critical, unknown)

generate_demo_substations(count)
  → Creates N demo substation objects
  → Returns List[Substation]

generate_demo_telemetry()
  → Generates realistic 24-hour data
  → Adds to substation readings
  → Returns List[TelemetryReading]

get_voltage_trend()
  → Extracts voltage time-series
  → Returns List[(timestamp_str, voltage)]

get_critical_substations()
  → Filters for CRITICAL status
  → Sorted by timestamp (newest first)

get_warning_substations()
  → Filters for WARNING status
  → Sorted by timestamp

get_sorted_substations()
  → All substations sorted by severity
  → Order: CRITICAL → WARNING → HEALTHY → UNKNOWN

refresh_all_substations()
  → Re-evaluates health for all
  → Updates each SubstationState

reset_all_data()
  → Clears all readings
  → Resets all states
```

**How to use:**
```python
from models import Thresholds
from service import generate_demo_substations, evaluate_health

substations = generate_demo_substations(8)
thresholds = Thresholds()

for sub in substations:
    reading = sub.get_latest_reading()
    if reading:
        health = evaluate_health(reading, thresholds)
        print(f"{sub.station_id}: {health.value}")
```

---

### main.py (~360 lines)
**Purpose:** Tkinter UI dashboard

**Contains:**
```
SubstationDashboard (Main Class)
  ├─ __init__() → Initialize UI
  ├─ _build_ui() → Create layout
  ├─ _build_summary_cards() → Fleet cards
  ├─ _build_substations_table() → Data tree
  ├─ _populate_substations_table() → Fill table
  ├─ _on_station_selected() → Row click handler
  ├─ _update_detail_panel() → Show details
  ├─ _draw_voltage_chart() → Plot chart
  ├─ _refresh_data() → Re-evaluate all
  └─ _reset_data() → Clear & regenerate

main() → Entry point
```

**UI Layout:**
```
┌─────────────────────────────────────────────┐
│ Title                    [Refresh] [Reset]  │
├─────────────────────────────────────────────┤
│  Left Panel             │   Right Panel      │
│                         │                    │
│  [Summary Cards]        │  [Detail Panel]    │
│  ┌─────────────────┐    │  ┌──────────────┐  │
│  │ Total: 8        │    │  │ Station ID   │  │
│  │ Healthy: 5      │    │  │ Status       │  │
│  │ Warning: 2      │    │  │ Latest V/T/L │  │
│  │ Critical: 1     │    │  │ Analysis     │  │
│  └─────────────────┘    │  └──────────────┘  │
│                         │                    │
│  [Substations Table]    │  [Voltage Chart]   │
│  ┌──────────────────┐   │  ┌──────────────┐  │
│  │ID │Loc│Status    │   │  │ ╱╲  ╱╲  ╱╲  │  │
│  │SUB-001│OK    │   │  │  │╱  ╲╱  ╲╱   │  │
│  │SUB-002│WARN  │   │  │  │          │  │  │
│  │SUB-003│CRIT  │   │  │  └──────────────┘  │
│  └──────────────────┘   │                    │
└─────────────────────────────────────────────┘
```

**How to run:**
```python
# In command line:
python main.py

# In code:
from main import main
main()
```

---

## 📚 Documentation Files

### README.md (Assessment Submission)
- **What**: Your official submission document
- **Who reads**: Evaluators
- **Length**: ~380 lines
- **Sections**: 5 required + extras

### FINAL_SUMMARY.md
- **What**: Overview of everything you have
- **Why**: Quick reference of what's included
- **Best for**: Understanding the big picture

### IMPLEMENTATION_SUMMARY.md
- **What**: Design decisions and architecture
- **Why**: Details on why choices were made
- **Best for**: Understanding code structure

### RUN_NOW.md
- **What**: 30-second quick start guide
- **Why**: Get the app running immediately
- **Best for**: First time running

### COMPLETION_CHECKLIST.md
- **What**: Step-by-step task tracker
- **Why**: Ensure nothing is missed
- **Best for**: Tracking progress to submission

### GIT_WORKFLOW.md
- **What**: GitHub branching strategy
- **Why**: Proper git practices
- **Best for**: Understanding commit conventions

### ASSESSMENT_PLAN.md (Legacy)
- **What**: Original assessment strategy
- **Why**: Strategic planning document
- **Best for**: Context about decisions

### QUICK_START.md (Legacy)
- **What**: Initial project setup guide
- **Why**: Getting oriented
- **Best for**: Understanding project structure

### FILE_REFERENCE.md
- **What**: This file!
- **Why**: Quick lookup of what's where
- **Best for**: Finding specific information

---

## 🗂️ Other Files

### requirements.txt
```
# Python 3.10+ Tkinter substations dashboard
# No external dependencies needed - uses stdlib only!

# For optional enhancements (not required):
# pytest==7.4.3           # For testing
# black==23.12.0          # For code formatting
# flake8==6.1.0           # For linting
```

### .gitignore
```
__pycache__/
*.pyc
.pytest_cache/
.vscode/
venv/
*.log
```

### data_generator.py (Legacy)
- Old data model demo generator
- Kept for reference
- Not used by new dashboard

### tests_models.py (Legacy)
- Example unit tests
- Kept for reference
- Models are testable despite no tests in submission

---

## 📊 Quick File Reference

| File | Lines | Type | Importance |
|------|-------|------|------------|
| **README.md** | ~380 | Submission | ⭐⭐⭐ MUST HAVE |
| **models.py** | ~180 | Code | ⭐⭐⭐ Core |
| **service.py** | ~220 | Code | ⭐⭐⭐ Core |
| **main.py** | ~360 | Code | ⭐⭐⭐ Core |
| FINAL_SUMMARY.md | ~350 | Doc | ⭐⭐ Reference |
| IMPLEMENTATION_SUMMARY.md | ~280 | Doc | ⭐⭐ Reference |
| RUN_NOW.md | ~150 | Doc | ⭐⭐ Quick Start |
| COMPLETION_CHECKLIST.md | ~250 | Doc | ⭐ Optional |
| GIT_WORKFLOW.md | ~300 | Doc | ⭐ Optional |
| requirements.txt | ~20 | Config | ⭐ Required |
| .gitignore | ~15 | Config | ⭐ Required |

---

## 🎯 Reading Guide by Role

### If You're the Developer (You!)
1. Start: **RUN_NOW.md** (get app running)
2. Then: **IMPLEMENTATION_SUMMARY.md** (understand design)
3. Review: **models.py**, **service.py**, **main.py** (read the code)
4. Reference: **COMPLETION_CHECKLIST.md** (track progress)

### If You're the Evaluator
1. Start: **README.md** (official documentation)
2. Review: **models.py**, **service.py** (code quality)
3. Run: `python main.py` (test functionality)
4. Watch: Video walkthrough (linked in README)

### If You're Extending This
1. Understand: **IMPLEMENTATION_SUMMARY.md**
2. Review: **models.py** (data structures)
3. Study: **service.py** (business logic)
4. Modify: **main.py** (UI changes)
5. Follow: **GIT_WORKFLOW.md** (commit standards)

---

## 🚀 Submission Preparation

### Minimum (What You MUST Have)
```
✓ models.py
✓ service.py
✓ main.py
✓ README.md (with 5 sections)
✓ requirements.txt
✓ .gitignore
✓ Video link (in README)
✓ GitHub repo (public)
```

### Recommended (What Makes it Better)
```
✓ Multiple commits with good messages
✓ This file directory reference
✓ Design documentation
✓ Completion checklist crossed off
✓ Professional README formatting
```

### Optional (Extra Credit)
```
✓ Unit tests
✓ Additional charts
✓ Advanced filtering
✓ Settings/config file
✓ Database integration
```

---

## 💾 Directory Structure

```
c:\Users\LENOVO\OneDrive\Desktop\assessment\
│
├── [SUBMIT TO GITHUB]
│   ├── README.md                    ⭐ MAIN SUBMISSION
│   ├── models.py                    ⭐ Core app
│   ├── service.py                   ⭐ Core app
│   ├── main.py                      ⭐ Core app
│   ├── requirements.txt
│   └── .gitignore
│
├── [REFERENCE DOCS]
│   ├── FINAL_SUMMARY.md
│   ├── IMPLEMENTATION_SUMMARY.md
│   ├── RUN_NOW.md
│   ├── COMPLETION_CHECKLIST.md
│   ├── GIT_WORKFLOW.md
│   ├── ASSESSMENT_PLAN.md
│   ├── QUICK_START.md
│   └── FILE_REFERENCE.md (this file)
│
└── [LEGACY/REFERENCE]
    ├── data_generator.py
    └── tests_models.py
```

---

## ✅ Next Steps

1. **Run It**: `python main.py`
2. **Understand**: Read IMPLEMENTATION_SUMMARY.md
3. **Record**: 2-3 min video demo
4. **Push**: `git push` to GitHub
5. **Submit**: Share GitHub link

You're all set! 🎉

---

**Questions about any file? Check the docstrings in the code or README.md!**
