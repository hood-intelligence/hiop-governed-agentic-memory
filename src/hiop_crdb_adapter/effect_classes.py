"""Canonical effects. Tool renames collapse here before HIOP mediation."""

from __future__ import annotations

from typing import Any

EFFECT_CATALOG: dict[str, dict[str, Any]] = {
    "telemetry.analyze": {"tier": "observe", "description": "Analyze streams (no physical effect)"},
    "lab.adjust_setpoint": {"tier": "benign", "description": "In-envelope lab setpoint change"},
    "spacecraft.maneuver": {"tier": "critical", "description": "Spacecraft maneuver — elevated only"},
    "payments.wire": {"tier": "critical", "description": "Financial wire — never auto from memory"},
}

ALIASES = {
    "telemetry.analyze": "telemetry.analyze",
    "analyze_sensors": "telemetry.analyze",
    "lab.adjust_setpoint": "lab.adjust_setpoint",
    "lab_setpoint_v2": "lab.adjust_setpoint",
    "spacecraft.maneuver": "spacecraft.maneuver",
    "orbit_nudge": "spacecraft.maneuver",
    "thruster.fire": "spacecraft.maneuver",
    "payments.wire": "payments.wire",
    "send_money": "payments.wire",
    "remembered_wire_api": "payments.wire",
}


def canonicalize(name: str) -> str | None:
    key = (name or "").strip().lower().replace(" ", "_")
    if key in ALIASES:
        return ALIASES[key]
    if key in EFFECT_CATALOG:
        return key
    for a, c in ALIASES.items():
        if a in key or key in a:
            return c
    return None
