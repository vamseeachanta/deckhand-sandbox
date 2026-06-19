# Self-contained dynacard runner: drives DynacardWorkflow.router directly
# with an in-memory cfg, so synthetic_card.mode is honoured without going
# through engine.py / ApplicationManager input-file resolution.
import json
import sys

from digitalmodel.marine_ops.artificial_lift.dynacard.solver import DynacardWorkflow

MODE = sys.argv[1] if len(sys.argv) > 1 else "FLUID_POUND"
SEED = int(sys.argv[2]) if len(sys.argv) > 2 else 712
OUT = sys.argv[3] if len(sys.argv) > 3 else "/tmp/fp-card.json"

cfg = {
    "basename": "artificial_lift",
    "synthetic_card": {"mode": MODE, "seed": SEED},
    "well": {
        "api14": f"SIM-{MODE}-{SEED}",
        "rod": {"diameter": 1.0, "length": 5000.0},
        "pump": {"diameter": 1.75, "depth": 5000.0},
        "surface_unit": {
            "manufacturer": "Sim",
            "unit_type": "Test",
            "stroke_length": 144.0,
            "gear_box_rating": 640000.0,
        },
        "spm": 10.0,
    },
    # No html report (avoids needing a result folder / visualization deps)
    "report": {"html": False},
}

wf = DynacardWorkflow()
out_cfg = wf.router(cfg)
results = out_cfg["results"]

# The surface card is what _apply_synthetic_card injected as well_data.surface_card
surface_card = cfg["well_data"]["surface_card"]
position = surface_card["position"]
load = surface_card["load"]

summary = {
    "mode": MODE,
    "seed": SEED,
    "api14": cfg["well_data"]["api14"],
    "position": position,
    "load": load,
    "n_points": len(position),
    "fillage": results.get("pump_fillage"),
    "fillage_pct_obj": (results.get("fillage") or {}).get("fillage"),
    "buckling_detected": results.get("buckling_detected"),
    "diagnostic_message": results.get("diagnostic_message"),
}

with open(OUT, "w") as f:
    json.dump(summary, f, indent=2)

print("MODE              :", MODE, "seed", SEED)
print("n position/load   :", len(position), "/", len(load))
print("pump_fillage      :", summary["fillage"])
print("fillage obj.pct   :", summary["fillage_pct_obj"])
print("buckling_detected :", summary["buckling_detected"])
print("diagnostic_message:", summary["diagnostic_message"])
print("written           :", OUT)
