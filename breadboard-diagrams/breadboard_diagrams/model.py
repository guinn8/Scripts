"""Physical holes, electrical strips, component pins and design checks.

Wires and module-internal ground connections are conductive edges. Resistors,
motors, capacitors and the potentiometer are deliberately NOT zero-ohm edges.
Crossing drawing paths never creates an electrical junction.
"""

from __future__ import annotations

import json
import re
from collections import defaultdict
from pathlib import Path


class DesignError(ValueError):
    pass


class UnionFind:
    def __init__(self):
        self.parents = {}

    def find(self, node):
        self.parents.setdefault(node, node)
        if self.parents[node] != node:
            self.parents[node] = self.find(self.parents[node])
        return self.parents[node]

    def union(self, a, b):
        a, b = self.find(a), self.find(b)
        if a != b:
            self.parents[b] = a


class Circuit:
    def __init__(self, path, parts_directory=None):
        self.path = Path(path).resolve()
        self.data = json.loads(self.path.read_text())
        self.parts_directory = Path(parts_directory or self.path.parent.parent / "parts")
        self.parts = {}
        self.boards = {}
        self.instances = {}
        self.pins = {}
        self.seats = {}
        self.occupancy = defaultdict(list)
        self.uf = UnionFind()
        for board in self.data["boards"]:
            part = self.part(board["part"])
            self.boards[board["id"]] = board | {"definition": part}
            for row in range(1, part["rows"] + 1):
                for strip in part["connected_strips"]:
                    nodes = [f'{board["id"]}:{col}{row}' for col in strip]
                    for node in nodes:
                        self.uf.union(nodes[0], node)
        for instance in self.data["instances"]:
            part = self.part(instance["part"])
            self.instances[instance["id"]] = instance | {"definition": part}
            if part["kind"] == "module":
                for header in part["headers"]:
                    for index, pin in enumerate(header["pins"]):
                        row = header["start_row"] + instance.get("row_shift", 0) + index
                        column = instance.get("column_map", {}).get(header["column"], header["column"])
                        node = f'{instance["board"]}:{column}{row}'
                        ref = f'{instance["id"]}.{pin}'
                        self.hole(node)
                        self.pins[ref] = node
                        self.seats[ref] = node
                        self.claim(node, ref)
                for group in part.get("internal_nets", []):
                    for pin in group[1:]:
                        self.uf.union(self.pins[f'{instance["id"]}.{group[0]}'],
                                      self.pins[f'{instance["id"]}.{pin}'])
            else:
                for pin in part["pins"]:
                    self.pins[f'{instance["id"]}.{pin}'] = f'{instance["id"]}.{pin}'
        for wire in self.data.get("wires", []):
            for side in ("from", "to"):
                ref = wire[side]
                node = self.resolve(ref)
                if ":" in node:
                    self.claim(node, wire["id"] + "." + side)
            self.uf.union(self.resolve(wire["from"]), self.resolve(wire["to"]))
        for component in self.data.get("passives", []):
            for side in ("a", "b"):
                self.claim(self.resolve(component[side]), component["id"] + "." + side)

    def part(self, name):
        if name not in self.parts:
            self.parts[name] = json.loads((self.parts_directory / f"{name}.json").read_text())
        return self.parts[name]

    def hole(self, ref):
        match = re.fullmatch(r"([^:]+):([A-J])(\d+)", ref)
        if not match or match[1] not in self.boards:
            raise DesignError(f"Invalid breadboard hole: {ref}")
        board = self.boards[match[1]]
        row = int(match[3])
        if not 1 <= row <= board["definition"]["rows"]:
            raise DesignError(f"Hole out of range: {ref}")
        return board, match[2], row

    def resolve(self, ref):
        if ref in self.pins:
            return self.pins[ref]
        if ":" in ref:
            self.hole(ref)
            return ref
        raise DesignError(f"Unknown component pin: {ref}")

    def claim(self, node, owner):
        self.hole(node)
        self.occupancy[node].append(owner)

    def xy(self, ref):
        if ref in self.pins and ":" not in self.pins[ref]:
            instance_id, pin = ref.split(".", 1)
            return tuple(self.instances[instance_id]["ports"][pin])
        node = self.resolve(ref)
        board, column, row = self.hole(node)
        definition = board["definition"]
        column_index = definition["columns"].index(column)
        return (board["origin"][0] + definition["column_pitch_units"][column_index] * board["pitch"],
                board["origin"][1] + (row - 1) * board["pitch"])

    def route(self, wire):
        return [self.xy(wire["from"]), *map(tuple, wire.get("via", [])), self.xy(wire["to"])]

    def connected(self, a, b):
        return self.uf.find(self.resolve(a)) == self.uf.find(self.resolve(b))

    def validate(self):
        errors = []
        for node, owners in self.occupancy.items():
            if len(owners) > 1:
                errors.append(f"Duplicate hole occupancy at {node}: {', '.join(owners)}")
        labels = dict(self.data.get("expected_nets", {}))
        # Include every exposed header pin, including the unconnected ones.
        for ref in self.seats:
            labels.setdefault(ref, "unused:" + ref)
        by_root = defaultdict(set)
        for ref, net in labels.items():
            by_root[self.uf.find(self.resolve(ref))].add(net)
        for nets in by_root.values():
            if len(nets) > 1:
                errors.append("Unexpected conductive connection: " + " / ".join(sorted(nets)))
        for group in self.data.get("required_connections", []):
            for ref in group[1:]:
                if not self.connected(group[0], ref):
                    errors.append(f"Open required connection: {group[0]} -> {ref}")
        for component in self.data.get("passives", []):
            if component["kind"] == "resistor":
                if component["ohms"] <= 0:
                    errors.append(f'{component["id"]}: resistor must have positive resistance')
            if component["kind"] in ("resistor", "capacitor"):
                if self.connected(component["a"], component["b"]):
                    errors.append(f'{component["id"]}: {component["kind"]} is bypassed by a conductive path')
                if "required_between" in component:
                    a, b = component["required_between"]
                    if not (self.connected(component["a"], a) and self.connected(component["b"], b)):
                        errors.append(f'{component["id"]}: {component["kind"]} does not join intended nets')
        for wire in self.data.get("wires", []):
            for x, y in self.route(wire):
                if not (0 <= x <= self.data["canvas"][0] and 0 <= y <= self.data["canvas"][1]):
                    errors.append(f'{wire["id"]}: route leaves canvas')
        if len(self.data.get("power_sources", [])) != 1:
            errors.append("This design requires exactly one declared power source")
        if errors:
            raise DesignError("\n".join(errors))
        return {
            "result": "pass",
            "boards": len(self.boards),
            "module_header_pins_checked": len(self.seats),
            "wires_checked": len(self.data.get("wires", [])),
            "occupied_holes_checked": len(self.occupancy),
            "required_connection_groups_checked": len(self.data.get("required_connections", [])),
            "checks": ["all exposed header pins", "breadboard strip connectivity", "unique hole occupancy",
                       "intended net separation", "required paths", "passives not treated as shorts",
                       "drawing route bounds", "one declared power source"],
            "not_verified": self.data.get("bench_unknowns", []),
        }
