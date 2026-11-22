"""Radar-specific wiring faults, including the crowded top-of-board interface."""

import csv
import io
import json
import tempfile
import unittest
from pathlib import Path

from breadboard_diagrams.model import Circuit, DesignError
from breadboard_diagrams.render import build_scene, export

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "circuits/radar-one-board.json"


class RadarTests(unittest.TestCase):
    def circuit(self, mutation=None):
        data = json.loads(SOURCE.read_text())
        if mutation:
            mutation(data)
        directory = tempfile.TemporaryDirectory()
        self.addCleanup(directory.cleanup)
        path = Path(directory.name) / "radar.json"
        path.write_text(json.dumps(data))
        return Circuit(path, ROOT / "parts")

    @staticmethod
    def wire(data, ident):
        return next(wire for wire in data["wires"] if wire["id"] == ident)

    def test_radar_uses_one_board_and_preserves_uart_pins(self):
        circuit = self.circuit()
        result = circuit.validate()
        self.assertEqual(result["boards"], 1)
        self.assertEqual(result["module_header_pins_checked"], 20)
        self.assertTrue(circuit.connected("radar.VCC", "nrf.VBUS"))
        self.assertTrue(circuit.connected("radar.C_R", "nrf.P0.15"))
        self.assertFalse(circuit.connected("radar.D_T", "nrf.P0.13"))
        self.assertTrue(circuit.connected("B:G3", "nrf.P0.13"))

    def test_power_from_logic_rail_is_rejected(self):
        def mutation(data):
            self.wire(data, "W1")["from"] = "B:A16"
        with self.assertRaisesRegex(DesignError, "LOGIC_VDD.*USB_5V"):
            self.circuit(mutation).validate()

    def test_neighbor_gpio_is_not_spare_supply_space(self):
        def mutation(data):
            self.wire(data, "W1")["from"] = "B:A14"
        with self.assertRaisesRegex(DesignError, "unused:nrf.P0.31"):
            self.circuit(mutation).validate()

    def test_transmit_pigtail_cannot_silently_use_another_gpio(self):
        def mutation(data):
            self.wire(data, "F4")["to"] = "B:J15"
        with self.assertRaisesRegex(DesignError, "unused:nrf.P0.17"):
            self.circuit(mutation).validate()

    def test_open_divider_junction_is_rejected(self):
        def mutation(data):
            data["wires"] = [w for w in data["wires"] if w["id"] != "J2"]
        with self.assertRaisesRegex(DesignError, "Open required connection"):
            self.circuit(mutation).validate()

    def test_resistor_bypass_is_rejected(self):
        def mutation(data):
            data["wires"].append({"id": "FAULT", "from": "B:B4", "to": "B:H4"})
        with self.assertRaisesRegex(DesignError, "resistor is bypassed"):
            self.circuit(mutation).validate()

    def test_capacitor_ground_must_reach_ground(self):
        def mutation(data):
            self.wire(data, "J4")["to"] = "B:B6"
        with self.assertRaisesRegex(DesignError, "Open required connection|capacitor does not join"):
            self.circuit(mutation).validate()

    def test_capacitor_on_same_strip_is_rejected(self):
        def mutation(data):
            next(p for p in data["passives"] if p["id"] == "C1")["b"] = "B:F5"
        with self.assertRaisesRegex(DesignError, "capacitor is bypassed"):
            self.circuit(mutation).validate()

    def test_pigtail_cannot_share_an_occupied_header_hole(self):
        def mutation(data):
            self.wire(data, "F4")["to"] = "nrf.P0.15"
        with self.assertRaisesRegex(DesignError, "Duplicate hole occupancy"):
            self.circuit(mutation).validate()

    def test_endpoint_clearance_catches_the_old_hidden_holes(self):
        def covered(circuit):
            result = []
            for passive in circuit.data["passives"]:
                drawing = passive["drawing"]
                cx, cy = drawing["body_center"]
                width, height = drawing["body_size"]
                for hole in circuit.occupancy:
                    x, y = circuit.xy(hole)
                    if cx-width/2 < x < cx+width/2 and cy-height/2 < y < cy+height/2:
                        result.append((passive["id"], hole))
            return result

        self.assertEqual(covered(self.circuit()), [])

        def old_holes(data):
            self.wire(data, "W3")["from"] = "B:H4"
            self.wire(data, "J4")["to"] = "B:E1"

        self.assertEqual(set(covered(self.circuit(old_holes))), {("R1", "B:H4"), ("R4", "B:E1")})

    def test_sensor_preview_and_capacitor_export_are_not_fader_defaults(self):
        circuit = self.circuit()
        svg = build_scene(circuit).svg()
        self.assertIn("DFRobot SEN0610", svg)
        self.assertNotIn(">FADER<", svg)
        self.assertIn('stroke-dasharray="10 8"', svg)
        directory = tempfile.TemporaryDirectory()
        self.addCleanup(directory.cleanup)
        export(SOURCE, directory.name, formats=("svg",))
        rows = list(csv.DictReader(io.StringIO((Path(directory.name) / "radar-one-board.wiring.csv").read_text())))
        self.assertEqual(next(row for row in rows if row["ID"] == "C1")["Value"], "100 nF ceramic")


if __name__ == "__main__":
    unittest.main()
