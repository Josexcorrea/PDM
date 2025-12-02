#!/usr/bin/env python3
"""
Test Cases for STM32 Simulator

Defines realistic test scenarios for FSAE race car PDM system.
Each scenario runs for 5 seconds, then returns to normal operation.
"""

from typing import Dict, List, Tuple


class TestScenario:
    """Base class for test scenarios"""

    def __init__(self, name: str, description: str):
        self.name = name
        self.description = description
        self.duration = 5.0  # seconds
        self.events = []  # List of (time, message) tuples

    def get_channel_states(self, elapsed_time: float) -> List[Dict]:
        """
        Returns channel states for given elapsed time.
        Must be implemented by subclasses.
        """
        raise NotImplementedError

    def get_event_at_time(self, elapsed_time: float) -> str:
        """Get the event message for current time"""
        current_event = "Normal operation"
        for event_time, message in self.events:
            if elapsed_time >= event_time:
                current_event = message
        return current_event


class CoolingFanFailure(TestScenario):
    """
    Scenario: Cooling fan connector comes loose during race

    Timeline:
    0-2s: Normal operation
    2s: Fan disconnects (loose connector)
    2-5s: Temperature rises, fan shows fault
    """

    def __init__(self):
        super().__init__(
            name="Cooling Fan Failure", description="Fan disconnects at 2s, temperature rises"
        )
        self.events = [
            (0.0, "Normal operation - all systems healthy"),
            (2.0, "Bump! Fan connector loosened"),
            (2.5, "Fan power dropping..."),
            (3.0, "Fan stopped - fault detected"),
            (3.5, "Temperature rising rapidly"),
            (4.0, "Warning: High temperature detected"),
            (4.5, "System continues running on reduced cooling"),
        ]

    def get_channel_states(self, elapsed_time: float) -> List[Dict]:
        """Generate realistic channel states based on timeline"""

        # Base states (normal operation)
        states = [
            {"voltage": 13.8, "current": 5.2, "temp": 45.0, "status": 0b00000001},  # ECU
            {"voltage": 13.8, "current": 3.5, "temp": 38.0, "status": 0b00000001},  # Fuel Pump
            {"voltage": 13.8, "current": 4.8, "temp": 42.0, "status": 0b00000001},  # Ignition
            {"voltage": 13.7, "current": 8.0, "temp": 35.0, "status": 0b00000001},  # Fan - starts ON
            {"voltage": 13.8, "current": 1.2, "temp": 32.0, "status": 0b00000001},  # DAQ
            {"voltage": 13.8, "current": 0.8, "temp": 30.0, "status": 0b00000001},  # Dashboard
            {"voltage": 13.8, "current": 2.1, "temp": 35.0, "status": 0b00000001},  # Sensors
            {"voltage": 13.7, "current": 0.0, "temp": 28.0, "status": 0b00000000},  # Starter - OFF
        ]

        # Fan failure progression
        if elapsed_time >= 2.0:
            # Fan connector loosening
            if elapsed_time < 2.5:
                states[3]["current"] = 8.0 * (1 - (elapsed_time - 2.0) / 0.5)  # Drop to 50%
            elif elapsed_time < 3.0:
                states[3]["current"] = 4.0 * (1 - (elapsed_time - 2.5) / 0.5)  # Drop to 0
            else:
                # Fan completely off with fault
                states[3]["current"] = 0.0
                states[3]["status"] = 0b00000010  # Fault flag set

        # Temperature rises when fan fails
        if elapsed_time >= 3.0:
            temp_increase = (elapsed_time - 3.0) * 5.0  # 5°C per second
            # All components get hotter
            for i in range(7):  # All except starter
                states[i]["temp"] += temp_increase

        return states


class EngineStartSequence(TestScenario):
    """
    Scenario: Normal engine start procedure

    Timeline:
    0-1s: Pre-start (only dash and sensors)
    1-3s: Starter motor cranking (high current, voltage drop)
    3s: Engine starts, all systems come online
    3-5s: Normal operation
    """

    def __init__(self):
        super().__init__(name="Engine Start Sequence", description="Starter engages at 1s, engine starts at 3s")
        self.events = [
            (0.0, "Pre-start: Dashboard and sensors only"),
            (1.0, "Starter motor engaged - cranking"),
            (1.5, "High current draw - voltage dropping"),
            (2.0, "Cranking continues..."),
            (2.5, "Engine almost started..."),
            (3.0, "Engine started! All systems online"),
            (3.5, "Systems stabilizing"),
            (4.0, "Normal operation restored"),
        ]

    def get_channel_states(self, elapsed_time: float) -> List[Dict]:
        """Generate realistic start sequence states"""

        # Initial state - only dash and sensors
        states = [
            {"voltage": 13.8, "current": 0.0, "temp": 25.0, "status": 0b00000000},  # ECU - OFF
            {"voltage": 13.8, "current": 0.0, "temp": 25.0, "status": 0b00000000},  # Fuel - OFF
            {"voltage": 13.8, "current": 0.0, "temp": 25.0, "status": 0b00000000},  # Ignition - OFF
            {"voltage": 13.8, "current": 0.0, "temp": 25.0, "status": 0b00000000},  # Fan - OFF
            {"voltage": 13.8, "current": 1.2, "temp": 25.0, "status": 0b00000001},  # DAQ - ON
            {"voltage": 13.8, "current": 0.8, "temp": 25.0, "status": 0b00000001},  # Dashboard - ON
            {"voltage": 13.8, "current": 2.1, "temp": 25.0, "status": 0b00000001},  # Sensors - ON
            {"voltage": 13.8, "current": 0.0, "temp": 25.0, "status": 0b00000000},  # Starter - OFF
        ]

        base_voltage = 13.8

        # Starter cranking (1-3s)
        if 1.0 <= elapsed_time < 3.0:
            # Starter ON with high current
            states[7]["status"] = 0b00000001
            states[7]["current"] = 150.0 + (elapsed_time - 1.0) * 10.0  # 150-170A

            # Voltage drops during cranking
            voltage_drop = 2.5  # Drop to ~11.3V
            for i in range(8):
                states[i]["voltage"] = base_voltage - voltage_drop

        # Engine starts (3s+)
        if elapsed_time >= 3.0:
            # Starter OFF
            states[7]["status"] = 0b00000000
            states[7]["current"] = 0.0

            # All systems come online
            states[0] = {"voltage": 13.8, "current": 5.2, "temp": 30.0, "status": 0b00000001}  # ECU
            states[1] = {"voltage": 13.8, "current": 3.5, "temp": 28.0, "status": 0b00000001}  # Fuel
            states[2] = {"voltage": 13.8, "current": 4.8, "temp": 32.0, "status": 0b00000001}  # Ignition
            # Fan stays off initially

            # Voltage recovers
            recovery = min(1.0, (elapsed_time - 3.0) / 0.5)
            for i in range(8):
                states[i]["voltage"] = base_voltage

        return states


# Scenario registry
SCENARIOS = {
    1: CoolingFanFailure(),
    2: EngineStartSequence(),
}


def get_scenario(scenario_id: int) -> TestScenario:
    """Get scenario by ID"""
    return SCENARIOS.get(scenario_id, None)


def list_scenarios() -> List[Tuple[int, str, str]]:
    """List all available scenarios"""
    return [(id, s.name, s.description) for id, s in SCENARIOS.items()]

