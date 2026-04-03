# 🚀 Quick Start: Run Your Dashboard in 30 Seconds

## 1. Launch the App

```bash
cd c:\Users\LENOVO\OneDrive\Desktop\assessment
python main.py
```

**Expected**: A window opens with a dashboard showing:
- Fleet Summary (4 colored cards)
- Table of 8 substations
- Detail panel (empty initially)
- Voltage chart area (empty initially)

## 2. Explore the Dashboard

### Click on a Substation
- Click any row in the table
- Detail panel updates on the right
- Voltage chart draws a 24-hour trend

### Try the Buttons
- **🔄 Refresh**: Re-evaluates all health statuses
- **🔴 Reset**: Clears and regenerates all demo data

## 3. Understanding the Colors

| Color | Meaning |
|-------|---------|
| 🟢 Green | Healthy (all metrics normal) |
| 🟡 Orange | Warning (approaching limits) |
| 🔴 Red | Critical (exceeding safe ranges) |
| ⚪ Gray | Unknown (no data) |

## 4. What You're Looking At

**Fleet Summary Cards** (top-left):
- Total: Count of all substations
- 🟢 Healthy: All good
- 🟡 Warning: Monitor these
- 🔴 Critical: Take action

**Substations Table** (left):
- Lists all stations sorted by severity
- Click to see details

**Detail Panel** (top-right):
- Station ID & location
- Latest readings (voltage, temp, load)
- Safety thresholds
- Health analysis

**Voltage Chart** (bottom-right):
- 24-hour voltage trend
- Shows grid lines and axis labels
- Updates when you select a station

## 5. File Structure Explained

```
assessment/
├── models.py          ← Data structures (what to store)
├── service.py         ← Business logic (how to evaluate)
├── main.py            ← UI (how to display)
├── README.md          ← Assessment documentation (SUBMIT THIS)
└── [other files]      ← Planning docs and guides
```

## 6. Key Code Concepts

### Health Status Decision Logic
```python
if temp > 85°C OR load > 95A:
    status = CRITICAL
elif temp > 70°C OR load > 80A:
    status = WARNING
else:
    status = HEALTHY
```

### Data Flow
```
Demo Telemetry Data
        ↓
Substation (stores readings)
        ↓
evaluate_health() (compute status)
        ↓
SubstationState (stores current status)
        ↓
Main.py (displays in UI)
```

## 7. For Your Assessment Submission

### Create GitHub Repo
```bash
git init
git add .
git commit -m "chore: initial substations dashboard"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/assessment.git
git push -u origin main
```

### Record Video (2-3 min)
1. Open dashboard
2. Show fleet overview
3. Click a WARNING/CRITICAL substation
4. Show detail panel + chart
5. Explain one design decision
6. Upload to YouTube (unlisted)
7. Update README with link

### Submit
- Share GitHub link with video link in README

## 8. Common Issues & Fixes

### "Python not found"
```bash
# Make sure Python 3.10+ installed
python --version  # Should be 3.10+
```

### "ModuleNotFoundError: No module named 'models'"
```bash
# Make sure you're in the right directory
cd c:\Users\LENOVO\OneDrive\Desktop\assessment
python main.py
```

### "No tkinter"
```bash
# Tkinter is built-in, but on Linux:
sudo apt-get install python3-tk
```

### App window is too small
```
Just resize the window—it's draggable
```

## 9. What to Talk About in Your Interview

**"Tell me about your architecture"**
- Models separate from logic separate from UI
- Easy to test, extend, swap frameworks

**"Why use dataclasses?"**
- Type hints, validation, slots for memory

**"How would you scale this?"**
- Database instead of in-memory
- Caching for large fleets
- WebSocket for real-time updates

**"What's one thing you'd change?"**
- See "Critical Reflection" in README.md

## 10. Next Steps

1. Run `python main.py` ✅
2. Click around and explore
3. Open models.py, service.py, main.py in editor
4. Read README.md (your submission document)
5. Record video walkthrough
6. Push to GitHub
7. Submit!

---

## Need Help?

- **README.md** → Full documentation
- **IMPLEMENTATION_SUMMARY.md** → Design details
- **models.py docstrings** → Data model explanation
- **service.py docstrings** → Business logic details

You've got this! 🎯
