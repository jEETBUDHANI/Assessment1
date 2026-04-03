"""
Unit tests for data model (models.py).

Run with: pytest tests/test_models.py -v

These tests demonstrate:
1. Validation works (invalid data rejected)
2. Status computation is correct
3. Query methods return expected results
"""

import pytest
from datetime import datetime, timedelta

from models import DeviceStatus, TelemetryReading, Substation, Facility


class TestTelemetryReading:
    """Validate that telemetry readings enforce constraints."""
    
    def test_valid_reading_creation(self):
        """Should create reading with valid values."""
        reading = TelemetryReading(
            timestamp=datetime.now(),
            voltage=240.0,
            current_load=50.0,
            temperature=45.0,
        )
        assert reading.voltage == 240.0
        assert reading.temperature == 45.0
    
    def test_invalid_voltage_too_high(self):
        """Should reject voltage > 1000V."""
        with pytest.raises(ValueError, match="Invalid voltage"):
            TelemetryReading(
                timestamp=datetime.now(),
                voltage=1001.0,  # Invalid
                current_load=50.0,
                temperature=45.0,
            )
    
    def test_invalid_voltage_negative(self):
        """Should reject negative voltage."""
        with pytest.raises(ValueError, match="Invalid voltage"):
            TelemetryReading(
                timestamp=datetime.now(),
                voltage=-5.0,  # Invalid
                current_load=50.0,
                temperature=45.0,
            )
    
    def test_invalid_temperature_too_high(self):
        """Should reject temperature > 100°C."""
        with pytest.raises(ValueError, match="Invalid temperature"):
            TelemetryReading(
                timestamp=datetime.now(),
                voltage=240.0,
                current_load=50.0,
                temperature=101.0,  # Invalid
            )
    
    def test_invalid_current_load_negative(self):
        """Should reject negative current load."""
        with pytest.raises(ValueError, match="Invalid current load"):
            TelemetryReading(
                timestamp=datetime.now(),
                voltage=240.0,
                current_load=-10.0,  # Invalid
                temperature=45.0,
            )


class TestSubstationStatus:
    """Test status computation logic."""
    
    def test_status_ok(self):
        """Should return OK when all metrics are normal."""
        sub = Substation(station_id="SUB-001", location="Test")
        reading = TelemetryReading(
            timestamp=datetime.now(),
            voltage=240.0,
            current_load=50.0,
            temperature=45.0,
        )
        sub.add_reading(reading)
        
        assert sub.status == DeviceStatus.OK
    
    def test_status_warning_high_temp(self):
        """Should return WARNING when temperature > 75°C."""
        sub = Substation(station_id="SUB-002", location="Test")
        reading = TelemetryReading(
            timestamp=datetime.now(),
            voltage=240.0,
            current_load=50.0,
            temperature=78.0,  # 75°C threshold
        )
        sub.add_reading(reading)
        
        assert sub.status == DeviceStatus.WARNING
    
    def test_status_warning_high_voltage(self):
        """Should return WARNING when voltage > 900V."""
        sub = Substation(station_id="SUB-003", location="Test")
        reading = TelemetryReading(
            timestamp=datetime.now(),
            voltage=920.0,  # 900V threshold
            current_load=50.0,
            temperature=45.0,
        )
        sub.add_reading(reading)
        
        assert sub.status == DeviceStatus.WARNING
    
    def test_status_critical_overtemp(self):
        """Should return CRITICAL when temperature > 85°C."""
        sub = Substation(station_id="SUB-004", location="Test")
        reading = TelemetryReading(
            timestamp=datetime.now(),
            voltage=240.0,
            current_load=50.0,
            temperature=88.0,  # 85°C threshold
        )
        sub.add_reading(reading)
        
        assert sub.status == DeviceStatus.CRITICAL
    
    def test_status_critical_overvoltage(self):
        """Should return CRITICAL when voltage > 950V."""
        sub = Substation(station_id="SUB-005", location="Test")
        reading = TelemetryReading(
            timestamp=datetime.now(),
            voltage=960.0,  # 950V threshold
            current_load=50.0,
            temperature=45.0,
        )
        sub.add_reading(reading)
        
        assert sub.status == DeviceStatus.CRITICAL
    
    def test_status_warning_no_readings(self):
        """Should return WARNING for unknown devices (no data)."""
        sub = Substation(station_id="SUB-006", location="Test")
        # No readings added
        
        assert sub.status == DeviceStatus.WARNING


class TestSubstationHistory:
    """Test telemetry history and query methods."""
    
    def test_add_reading(self):
        """Should append readings to history."""
        sub = Substation(station_id="SUB-001", location="Test")
        
        r1 = TelemetryReading(
            timestamp=datetime.now(),
            voltage=240.0,
            current_load=50.0,
            temperature=45.0,
        )
        sub.add_reading(r1)
        
        assert len(sub.readings) == 1
        assert sub.latest_reading == r1
    
    def test_latest_reading(self):
        """Should return most recent reading."""
        sub = Substation(station_id="SUB-001", location="Test")
        now = datetime.now()
        
        r1 = TelemetryReading(timestamp=now - timedelta(hours=1), 
                             voltage=240.0, current_load=50.0, temperature=45.0)
        r2 = TelemetryReading(timestamp=now, 
                             voltage=242.0, current_load=51.0, temperature=46.0)
        
        sub.add_reading(r1)
        sub.add_reading(r2)
        
        assert sub.latest_reading == r2
    
    def test_get_readings_since(self):
        """Should filter readings by timestamp."""
        sub = Substation(station_id="SUB-001", location="Test")
        now = datetime.now()
        
        r1 = TelemetryReading(timestamp=now - timedelta(hours=2), 
                             voltage=240.0, current_load=50.0, temperature=45.0)
        r2 = TelemetryReading(timestamp=now - timedelta(hours=1), 
                             voltage=241.0, current_load=50.5, temperature=45.5)
        r3 = TelemetryReading(timestamp=now, 
                             voltage=242.0, current_load=51.0, temperature=46.0)
        
        sub.add_reading(r1)
        sub.add_reading(r2)
        sub.add_reading(r3)
        
        # Get readings from last hour
        last_hour = sub.get_readings_since(now - timedelta(hours=1))
        assert len(last_hour) == 2
        assert r1 not in last_hour
        assert r2 in last_hour
        assert r3 in last_hour


class TestFacility:
    """Test facility-level queries."""
    
    def test_add_substation(self):
        """Should register new substations."""
        facility = Facility()
        sub = Substation(station_id="SUB-001", location="Test")
        
        facility.add_substation(sub)
        
        assert len(facility.substations) == 1
    
    def test_get_critical_stations(self):
        """Should return only CRITICAL substations."""
        facility = Facility()
        
        ok_sub = Substation(station_id="SUB-001", location="OK")
        ok_sub.add_reading(TelemetryReading(
            timestamp=datetime.now(),
            voltage=240.0, current_load=50.0, temperature=45.0
        ))
        
        crit_sub = Substation(station_id="SUB-002", location="Critical")
        crit_sub.add_reading(TelemetryReading(
            timestamp=datetime.now(),
            voltage=960.0, current_load=50.0, temperature=45.0  # Overvoltage
        ))
        
        facility.add_substation(ok_sub)
        facility.add_substation(crit_sub)
        
        critical = facility.get_critical_stations()
        assert len(critical) == 1
        assert critical[0].station_id == "SUB-002"
    
    def test_get_warning_stations(self):
        """Should return only WARNING substations."""
        facility = Facility()
        
        ok_sub = Substation(station_id="SUB-001", location="OK")
        ok_sub.add_reading(TelemetryReading(
            timestamp=datetime.now(),
            voltage=240.0, current_load=50.0, temperature=45.0
        ))
        
        warn_sub = Substation(station_id="SUB-002", location="Warning")
        warn_sub.add_reading(TelemetryReading(
            timestamp=datetime.now(),
            voltage=240.0, current_load=50.0, temperature=78.0  # High temp
        ))
        
        facility.add_substation(ok_sub)
        facility.add_substation(warn_sub)
        
        warnings = facility.get_warning_stations()
        assert len(warnings) == 1
        assert warnings[0].station_id == "SUB-002"
    
    def test_get_station_by_id(self):
        """Should retrieve specific substation by ID."""
        facility = Facility()
        
        sub1 = Substation(station_id="SUB-001", location="Location 1")
        sub2 = Substation(station_id="SUB-002", location="Location 2")
        
        facility.add_substation(sub1)
        facility.add_substation(sub2)
        
        found = facility.get_station_by_id("SUB-002")
        assert found.location == "Location 2"
    
    def test_get_all_stations_sorted(self):
        """Should sort by severity: CRITICAL → WARNING → OK."""
        facility = Facility()
        
        ok_sub = Substation(station_id="SUB-001", location="OK")
        ok_sub.add_reading(TelemetryReading(
            timestamp=datetime.now(),
            voltage=240.0, current_load=50.0, temperature=45.0
        ))
        
        warn_sub = Substation(station_id="SUB-002", location="Warning")
        warn_sub.add_reading(TelemetryReading(
            timestamp=datetime.now(),
            voltage=240.0, current_load=50.0, temperature=78.0
        ))
        
        crit_sub = Substation(station_id="SUB-003", location="Critical")
        crit_sub.add_reading(TelemetryReading(
            timestamp=datetime.now(),
            voltage=960.0, current_load=50.0, temperature=45.0
        ))
        
        facility.add_substation(ok_sub)
        facility.add_substation(warn_sub)
        facility.add_substation(crit_sub)
        
        sorted_subs = facility.get_all_stations_sorted()
        
        # Should be CRITICAL, WARNING, OK
        assert sorted_subs[0].station_id == "SUB-003"
        assert sorted_subs[1].station_id == "SUB-002"
        assert sorted_subs[2].station_id == "SUB-001"
