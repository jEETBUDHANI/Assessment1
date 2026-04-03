"""
Sample data generator for testing and demos.

Creates realistic telemetry data for 5 substations with various
status conditions (OK, WARNING, CRITICAL).
"""

import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict, Any

from models import Substation, TelemetryReading, Facility, DeviceStatus


def generate_sample_readings(
    hours_back: int = 24,
    interval_minutes: int = 30,
    base_voltage: float = 240.0,
    base_temp: float = 45.0,
) -> List[TelemetryReading]:
    """
    Generate realistic telemetry readings over time.
    
    Args:
        hours_back: How far back to generate data (default 24 hours)
        interval_minutes: Reading frequency (default 30 min)
        base_voltage: Starting voltage (nominal ~240V)
        base_temp: Starting temperature (nominal ~45°C)
    
    Returns:
        List of TelemetryReading objects
    """
    readings = []
    now = datetime.now()
    start = now - timedelta(hours=hours_back)
    
    temp = start
    voltage = base_voltage
    temperature = base_temp
    
    while temp <= now:
        # Simulate natural drift with some randomness
        import random
        voltage += random.uniform(-2, 2)  # ±2V drift
        temperature += random.uniform(-1, 1)  # ±1°C drift
        
        # Add some noise
        voltage = max(0, min(1000, voltage))  # Clamp to valid range
        temperature = max(0, min(100, temperature))
        
        current_load = 50 + random.uniform(-10, 10)  # ~50A ±10
        
        reading = TelemetryReading(
            timestamp=temp,
            voltage=round(voltage, 2),
            current_load=round(current_load, 2),
            temperature=round(temperature, 2),
        )
        readings.append(reading)
        temp += timedelta(minutes=interval_minutes)
    
    return readings


def create_sample_facility() -> Facility:
    """
    Create a facility with 5 substations in different states.
    
    Returns:
        Facility object ready for testing
    """
    facility = Facility()
    
    # Substation 1: OK - Normal operation
    sub1 = Substation(station_id="SUB-001", location="North District")
    sub1.readings.extend(generate_sample_readings(
        hours_back=24,
        base_voltage=240.0,
        base_temp=50.0,
    ))
    facility.add_substation(sub1)
    
    # Substation 2: WARNING - Running warm
    sub2 = Substation(station_id="SUB-002", location="Central Hub")
    readings2 = generate_sample_readings(
        hours_back=24,
        base_voltage=245.0,
        base_temp=78.0,  # Higher baseline
    )
    sub2.readings.extend(readings2)
    facility.add_substation(sub2)
    
    # Substation 3: CRITICAL - Overheating
    sub3 = Substation(station_id="SUB-003", location="East Valley")
    readings3 = generate_sample_readings(
        hours_back=24,
        base_voltage=960.0,  # High voltage
        base_temp=88.0,  # Overheating
    )
    sub3.readings.extend(readings3)
    facility.add_substation(sub3)
    
    # Substation 4: OK - Recently added
    sub4 = Substation(station_id="SUB-004", location="West Coast")
    sub4.readings.extend(generate_sample_readings(
        hours_back=6,  # Shorter history
        base_voltage=238.0,
        base_temp=52.0,
    ))
    facility.add_substation(sub4)
    
    # Substation 5: WARNING - Trending up (potential issue)
    sub5 = Substation(station_id="SUB-005", location="Industrial Zone")
    readings5 = generate_sample_readings(
        hours_back=24,
        base_voltage=255.0,  # Over nominal
        base_temp=72.0,
    )
    sub5.readings.extend(readings5)
    facility.add_substation(sub5)
    
    return facility


def save_facility_as_json(facility: Facility, filepath: str) -> None:
    """
    Serialize facility to JSON for persistence and testing.
    
    Args:
        facility: Facility object to serialize
        filepath: Output file path
    """
    data = {
        "substations": []
    }
    
    for sub in facility.substations:
        sub_data = {
            "station_id": sub.station_id,
            "location": sub.location,
            "readings": [
                {
                    "timestamp": r.timestamp.isoformat(),
                    "voltage": r.voltage,
                    "current_load": r.current_load,
                    "temperature": r.temperature,
                }
                for r in sub.readings
            ]
        }
        data["substations"].append(sub_data)
    
    Path(filepath).parent.mkdir(parents=True, exist_ok=True)
    with open(filepath, "w") as f:
        json.dump(data, f, indent=2)
    
    print(f"✓ Sample data saved to {filepath}")


def load_facility_from_json(filepath: str) -> Facility:
    """
    Deserialize facility from JSON.
    
    Args:
        filepath: Input JSON file
    
    Returns:
        Reconstructed Facility object
    """
    with open(filepath, "r") as f:
        data = json.load(f)
    
    facility = Facility()
    
    for sub_data in data["substations"]:
        sub = Substation(
            station_id=sub_data["station_id"],
            location=sub_data["location"],
        )
        
        for reading_data in sub_data["readings"]:
            reading = TelemetryReading(
                timestamp=datetime.fromisoformat(reading_data["timestamp"]),
                voltage=reading_data["voltage"],
                current_load=reading_data["current_load"],
                temperature=reading_data["temperature"],
            )
            sub.add_reading(reading)
        
        facility.add_substation(sub)
    
    return facility


def print_facility_summary(facility: Facility) -> None:
    """Print a human-readable summary of facility status."""
    print("\n" + "="*60)
    print(f"FACILITY SUMMARY: {len(facility.substations)} substations")
    print("="*60)
    
    print(f"\n🔴 CRITICAL: {len(facility.get_critical_stations())}")
    for sub in facility.get_critical_stations():
        print(f"   {sub.station_id} ({sub.location})")
        if sub.latest_reading:
            print(f"      Temp: {sub.latest_reading.temperature}°C, Voltage: {sub.latest_reading.voltage}V")
    
    print(f"\n🟡 WARNING: {len(facility.get_warning_stations())}")
    for sub in facility.get_warning_stations():
        print(f"   {sub.station_id} ({sub.location})")
        if sub.latest_reading:
            print(f"      Temp: {sub.latest_reading.temperature}°C, Voltage: {sub.latest_reading.voltage}V")
    
    print(f"\n🟢 OK: {len(facility.get_ok_stations())}")
    for sub in facility.get_ok_stations():
        print(f"   {sub.station_id} ({sub.location})")
    
    print("\n" + "="*60 + "\n")


if __name__ == "__main__":
    # Generate and save sample data
    print("Generating sample telemetry data...")
    facility = create_sample_facility()
    print_facility_summary(facility)
    
    # Save to JSON
    output_path = "sample_telemetry.json"
    save_facility_as_json(facility, output_path)
    
    # Verify by loading back
    print("Verifying JSON serialization...")
    loaded = load_facility_from_json(output_path)
    print_facility_summary(loaded)
