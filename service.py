"""
Business logic service functions for substations telemetry dashboard.

Pure functions with no UI dependencies. All logic is testable and reproducible.
These functions handle health evaluation, data ingestion, and statistics.
"""

from datetime import datetime, timedelta
from random import uniform, randint
from typing import List, Tuple

from models import (
    HealthStatus,
    TelemetryReading,
    Thresholds,
    Substation,
    SubstationState,
    FleetSnapshot,
)


def evaluate_health(reading: TelemetryReading, thresholds: Thresholds) -> HealthStatus:
    """
    Evaluate substation health based on telemetry and thresholds.
    
    Decision logic:
    1. CRITICAL if any metric exceeds critical threshold
    2. WARNING if any metric exceeds warning threshold
    3. HEALTHY otherwise
    
    Args:
        reading: Current telemetry measurement
        thresholds: Safety threshold configuration
    
    Returns:
        HealthStatus enum value
    """
    # Check critical conditions
    if (reading.temperature > thresholds.temperature_crit or
        reading.load > thresholds.load_crit or
        reading.voltage < thresholds.voltage_min or
        reading.voltage > thresholds.voltage_max):
        return HealthStatus.CRITICAL
    
    # Check warning conditions
    if (reading.temperature > thresholds.temperature_warn or
        reading.load > thresholds.load_warn or
        reading.voltage > thresholds.voltage_warn):
        return HealthStatus.WARNING
    
    return HealthStatus.HEALTHY


def ingest_reading(
    substation: Substation,
    reading: TelemetryReading,
    thresholds: Thresholds,
) -> HealthStatus:
    """
    Add new telemetry reading to substation and update health status.
    
    Side effect: Modifies substation state and adds reading to history.
    
    Args:
        substation: Substation to update
        reading: New telemetry data
        thresholds: Configuration for health evaluation
    
    Returns:
        Computed health status
    """
    health = evaluate_health(reading, thresholds)
    substation.add_reading(reading)
    substation.state.update_reading(reading, health)
    return health


def count_health_statuses(substations: List[Substation]) -> Tuple[int, int, int, int]:
    """
    Count substations by health status.
    
    Args:
        substations: List of substations to analyze
    
    Returns:
        Tuple of (healthy_count, warning_count, critical_count, unknown_count)
    """
    healthy = sum(1 for s in substations if s.state.health == HealthStatus.HEALTHY)
    warning = sum(1 for s in substations if s.state.health == HealthStatus.WARNING)
    critical = sum(1 for s in substations if s.state.health == HealthStatus.CRITICAL)
    unknown = sum(1 for s in substations if s.state.health == HealthStatus.UNKNOWN)
    
    return healthy, warning, critical, unknown


def create_fleet_snapshot(substations: List[Substation]) -> FleetSnapshot:
    """
    Create a summary snapshot of entire fleet health.
    
    Args:
        substations: List of all monitored substations
    
    Returns:
        FleetSnapshot with aggregated statistics
    """
    healthy, warning, critical, unknown = count_health_statuses(substations)
    
    return FleetSnapshot(
        total_substations=len(substations),
        healthy_count=healthy,
        warning_count=warning,
        critical_count=critical,
        unknown_count=unknown,
    )


def generate_demo_substations(count: int = 5) -> List[Substation]:
    """
    Create demo substations for testing and visualization.
    
    Args:
        count: Number of substations to generate
    
    Returns:
        List of demo Substation objects with realistic data
    """
    demo_locations = [
        "North District", "Central Hub", "East Valley",
        "West Coast", "South Industrial", "Downtown Core",
        "Suburban Plaza", "Airport Zone", "Harbor Facility", "Mountain Ridge"
    ]
    
    substations = []
    for i in range(count):
        station_id = f"SUB-{i+1:03d}"
        location = demo_locations[i % len(demo_locations)]
        substation = Substation(station_id=station_id, location=location)
        substations.append(substation)
    
    return substations


def generate_demo_telemetry(
    substation: Substation,
    hours: int = 24,
    interval_minutes: int = 30,
    base_voltage: float = 230.0,
    base_temperature: float = 45.0,
    base_load: float = 50.0,
) -> List[TelemetryReading]:
    """
    Generate realistic demo telemetry data for a substation.
    
    Creates realistic time-series data with drift and noise.
    
    Args:
        substation: Substation to populate
        hours: Hours of historical data to generate
        interval_minutes: Interval between readings
        base_voltage: Starting voltage (nominal)
        base_temperature: Starting temperature
        base_load: Starting load
    
    Returns:
        List of generated readings
    """
    readings = []
    now = datetime.now()
    start = now - timedelta(hours=hours)
    current_time = start
    
    voltage = base_voltage
    temperature = base_temperature
    load = base_load
    
    while current_time <= now:
        # Simulate natural drift with randomness
        voltage += uniform(-1.5, 1.5)
        temperature += uniform(-0.5, 0.5)
        load += uniform(-2, 2)
        
        # Clamp to valid ranges
        voltage = max(190, min(270, voltage))
        temperature = max(20, min(95, temperature))
        load = max(10, min(100, load))
        
        reading = TelemetryReading(
            timestamp=current_time,
            voltage=round(voltage, 2),
            temperature=round(temperature, 2),
            load=round(load, 2),
        )
        
        readings.append(reading)
        substation.add_reading(reading)
        current_time += timedelta(minutes=interval_minutes)
    
    return readings


def refresh_all_substations(
    substations: List[Substation],
    thresholds: Thresholds,
) -> None:
    """
    Refresh health status for all substations based on latest reading.
    
    Side effect: Updates SubstationState for each substation.
    
    Args:
        substations: List of substations to refresh
        thresholds: Health evaluation thresholds
    """
    for substation in substations:
        latest = substation.get_latest_reading()
        if latest:
            health = evaluate_health(latest, thresholds)
            substation.state.update_reading(latest, health)


def get_critical_substations(substations: List[Substation]) -> List[Substation]:
    """
    Get all substations with CRITICAL health status.
    
    Args:
        substations: List to filter
    
    Returns:
        Substations with CRITICAL status, sorted by timestamp (newest first)
    """
    critical = [s for s in substations if s.state.health == HealthStatus.CRITICAL]
    return sorted(
        critical,
        key=lambda s: s.state.last_update or datetime.min,
        reverse=True
    )


def get_warning_substations(substations: List[Substation]) -> List[Substation]:
    """
    Get all substations with WARNING health status.
    
    Args:
        substations: List to filter
    
    Returns:
        Substations with WARNING status, sorted by timestamp (newest first)
    """
    warning = [s for s in substations if s.state.health == HealthStatus.WARNING]
    return sorted(
        warning,
        key=lambda s: s.state.last_update or datetime.min,
        reverse=True
    )


def get_sorted_substations(substations: List[Substation]) -> List[Substation]:
    """
    Get all substations sorted by health severity.
    
    Order: CRITICAL → WARNING → HEALTHY → UNKNOWN
    
    Args:
        substations: List to sort
    
    Returns:
        Sorted substations (failures first)
    """
    critical = get_critical_substations(substations)
    warning = get_warning_substations(substations)
    healthy = [s for s in substations if s.state.health == HealthStatus.HEALTHY]
    unknown = [s for s in substations if s.state.health == HealthStatus.UNKNOWN]
    
    return critical + warning + healthy + unknown


def get_voltage_trend(substation: Substation, hours: int = 24) -> List[Tuple[str, float]]:
    """
    Get voltage trend data for charting.
    
    Args:
        substation: Substation to analyze
        hours: Time window
    
    Returns:
        List of (timestamp_str, voltage) tuples
    """
    readings = substation.get_readings_in_window(hours)
    if not readings:
        return []
    
    return [(r.timestamp.strftime("%H:%M"), r.voltage) for r in readings]


def reset_all_data(substations: List[Substation]) -> None:
    """
    Clear all telemetry data from all substations.
    
    Side effect: Resets readings list and state for each substation.
    
    Args:
        substations: List to reset
    """
    for substation in substations:
        substation.readings.clear()
        substation.state = SubstationState(
            station_id=substation.station_id,
            location=substation.location,
        )
