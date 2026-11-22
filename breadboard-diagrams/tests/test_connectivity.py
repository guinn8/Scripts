"""Fault injections for the errors this drawing is supposed to prevent."""

import json
import tempfile
import unittest
from pathlib import Path

from breadboard_diagrams.model import Circuit, DesignError

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "circuits/slider-single-usb.json"


class ConnectivityTests(unittest.TestCase):
    def circuit(self, mutation=None):
        data = json.loads(SOURCE.read_text())
        if mutation:
            mutation(data)
        directory = tempfile.TemporaryDirectory()
        self.addCleanup(directory.cleanup)
        path = Path(directory.name) / "circuit.json"
        path.write_text(json.dumps(data))
        return Circuit(path, ROOT / "parts")

    def test_single_usb_circuit_passes(self):
        circuit = self.circuit()
        result = circuit.validate()
        self.assertEqual(result["module_header_pins_checked"], 36)
        self.assertTrue(circuit.connected("nrf.VBUS", "driver.VM"))
        self.assertFalse(circuit.connected("nrf.VBUS", "nrf.VDD_OUT"))
        self.assertFalse(circuit.connected("driver.STBY", "driver.GND_C"))

    def test_same_parts_work_for_an_independent_second_circuit(self):
        from breadboard_diagrams.render import build_scene
        import xml.etree.ElementTree as ET
        circuit = Circuit(ROOT / "examples/vbus-tap.json", ROOT / "parts")
        self.assertEqual(circuit.validate()["module_header_pins_checked"], 20)
        root = ET.fromstring(build_scene(circuit).svg())
        self.assertEqual(root.tag, "{http://www.w3.org/2000/svg}svg")

    def test_motor_supply_into_logic_rail_is_rejected(self):
        def mutation(data):
            data["wires"][0]["to"] = "U:H16"
        with self.assertRaisesRegex(DesignError, "LOGIC_VDD.*USB_5V"):
            self.circuit(mutation).validate()

    def test_adjacent_unused_gpio_is_not_a_free_power_strip(self):
        def mutation(data):
            data["wires"][0]["from"] = "L:B14"
        with self.assertRaisesRegex(DesignError, "unused:nrf.P0.31"):
            self.circuit(mutation).validate()

    def test_missing_common_ground_is_rejected(self):
        def mutation(data):
            data["wires"] = [wire for wire in data["wires"] if wire["id"] != "W3"]
        with self.assertRaisesRegex(DesignError, "Open required connection"):
            self.circuit(mutation).validate()

    def test_duplicate_hole_is_rejected_even_on_same_net(self):
        def mutation(data):
            data["wires"][0]["from"] = "L:C17"
        with self.assertRaisesRegex(DesignError, "Duplicate hole occupancy"):
            self.circuit(mutation).validate()

    def test_wrong_half_of_row_breaks_signal(self):
        def mutation(data):
            data["wires"][3]["to"] = "U:A8"
        with self.assertRaises(DesignError):
            self.circuit(mutation).validate()

    def test_incorrect_pulldown_connection_is_rejected(self):
        def mutation(data):
            data["passives"][0]["b"] = "U:I14"
        with self.assertRaisesRegex(DesignError, "resistor does not join intended nets"):
            self.circuit(mutation).validate()

    def test_diagram_crossings_are_not_junctions(self):
        def mutation(data):
            data["wires"][0]["via"] = [[390, 1000], [390, 774], [780, 774], [780, 716]]
        circuit = self.circuit(mutation)
        circuit.validate()
        self.assertFalse(circuit.connected("nrf.VBUS", "nrf.VDD_OUT"))

    def test_out_of_range_hole_rejected(self):
        def mutation(data):
            data["wires"][0]["from"] = "L:B18"
        with self.assertRaisesRegex(DesignError, "out of range"):
            self.circuit(mutation)


if __name__ == "__main__":
    unittest.main()
