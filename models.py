"""
Data models for substations telemetry monitoring dashboard.

Pure data models with no UI dependencies. Uses Python 3.10+ dataclasses
with slots=True for memory efficiency. All validation happens at creation time.
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import List, Optional


class HealthStatus(Enum):
    """Overall health status of a substation."""
    HEALTHY = "healthy"
    WARNING = "warning"
    CRITICAL = "critical"
    UNKNOWN = "unknown"


@dataclass(slots=True)
class Thresholds:
    """
    Safety thresholds for telemetry readings.
    
    Used to classify substation health. Levels define when a reading
    moves from HEALTHY → WARNING → CRITICAL.
    """
    voltage_min: float = 200.0      # Volts (minimum safe)
    voltage_max: float = 260.0      # Volts (maximum safe)
    voltage_warn: float = 250.0     # Volts (warning threshold)
    
    temperature_warn: float = 70.0  # Celsius (warning threshold)
    temperature_crit: float = 85.0  # Celsius (critical threshold)
    
    load_warn: float = 80.0         # Amperes (warning threshold)
    load_crit: float = 95.0         # Amperes (critical threshold)
    
    def __post_init__(self):
        """Validate threshold constraints."""
        if not (0 <= self.voltage_min < self.voltage_max):
            raise ValueError(f"Invalid voltage thresholds: min={self.voltage_min}, max={self.voltage_max}")
        if not (0 <= self.temperature_warn < self.temperature_crit):
            raise ValueError(f"Invalid temperature thresholds: warn={self.temperature_warn}, crit={self.temperature_crit}")
        if not (0 <= self.load_warn < self.load_crit):
            raise ValueError(f"Invalid load thresholds: warn={self.load_warn}, crit={self.load_crit}")


@dataclass(slots=True, frozen=True)
class TelemetryReading:
    """
    Single immutable telemetry snapshot from a substation.
    
    Represents one moment in time. Immutable (frozen=True) prevents
    accidental mutations. All readings are historical facts.
    """
    timestamp: datetime
    voltage: float      # Volts
    temperature: float  # Celsius
    load: float         # Amperes
    
    def __post_init__(self):
        """Validate reading values."""
        if not (0 <= self.voltage <= 1000):
            raise ValueError(f"Invalid voltage: {self.voltage}V")
        if not (0 <= self.temperature <= 100):
            raise ValueError(f"Invalid temperature: {self.temperature}°C")
        if not (0 <= self.load <= 200):
            raise ValueError(f"Invalid load: {self.load}A")


@dataclass(slots=True)
class SubstationState:
    """
    Current operational state of a substation.
    
    Mutable snapshot of a substation's latest health, readings, and status.
    Updated each time new telemetry arrives.
    """
    station_id: str
    location: str
    health: HealthStatus = HealthStatus.UNKNOWN
    latest_reading: Optional[TelemetryReading] = None
    last_update: Optional[datetime] = None
    reading_count: int = 0
    
    def update_reading(self, reading: TelemetryReading, health: HealthStatus) -> None:
        """
        Update state with new telemetry reading and computed health.
        
        Args:
            reading: New telemetry measurement
            health: Computed health status based on reading vs thresholds
        """
        self.latest_reading = reading
        self.health = health
        self.last_update = reading.timestamp
        self.reading_count += 1
    
    def get_status_color(self) -> str:
        """Return color code for UI display based on health status."""
        colors = {
            HealthStatus.HEALTHY: "#00AA00",   # Green
            HealthStatus.WARNING: "#FFAA00",   # Orange
            HealthStatus.CRITICAL: "#DD0000",  # Red
            HealthStatus.UNKNOWN: "#888888",   # Gray
        }
        return colors.get(self.health, "#888888")


@dataclass(slots=True)
class Substation:
    """
    Complete substation entity with identity and telemetry history.
    
    Represents a monitored power substation with all its readings
    and current operational state.
    """
    station_id: str
    location: str
    readings: List[TelemetryReading] = field(default_factory=list)
    state: SubstationState = field(init=False)
    
    def __post_init__(self):
        """Initialize substation with default state."""
        self.state = SubstationState(
            station_id=self.station_id,
            location=self.location,
        )
    
    def add_reading(self, reading: TelemetryReading) -> None:
        """Append new telemetry reading to history."""
        self.readings.append(reading)
    
    def get_latest_reading(self) -> Optional[TelemetryReading]:
        """Retrieve most recent telemetry reading."""
        return self.readings[-1] if self.readings else None
    
    def get_readings_in_window(self, hours: int = 24) -> List[TelemetryReading]:
        """
        Get all readings from last N hours.
        
        Useful for charts and trend analysis.
        """
        if not self.readings:
            return []
        
        now = datetime.now()
        cutoff = datetime.fromtimestamp(now.timestamp() - (hours * 3600))
        return [r for r in self.readings if r.timestamp >= cutoff]
    
    def __repr__(self) -> str:
        status = self.state.health.value if self.state else "unknown"
        return f"Substation({self.station_id}, location={self.location}, status={status})"


@dataclass(slots=True)
class FleetSnapshot:
    """
    Snapshot of entire facility health at a point in time.
    
    Used for dashboard summaries and statistics.
    """
    total_substations: int
    healthy_count: int
    warning_count: int
    critical_count: int
    unknown_count: int
    timestamp: datetime = field(default_factory=datetime.now)
    
    @property
    def healthy_percentage(self) -> float:
        """Calculate percentage of healthy substations."""
        if self.total_substations == 0:
            return 0.0
        return (self.healthy_count / self.total_substations) * 100
    
    @property
    def issues_count(self) -> int:
        """Total count of warning + critical substations."""
        return self.warning_count + self.critical_count
