# Generate a FLUID_POUND card diagnosed by the LEGACY threshold classifier
# (forces PumpDiagnostics._load_model -> None so the shipped mis-calibrated ML
# model is bypassed and the rule-based classifier names fluid pound correctly).
import json, sys
from digitalmodel.marine_ops.artificial_lift.dynacard.diagnostics import PumpDiagnostics
PumpDiagnostics._load_model = classmethod(lambda cls: None)   # legacy threshold path
from digitalmodel.marine_ops.artificial_lift.dynacard.solver import DynacardWorkflow

MODE = "FLUID_POUND"; SEED = int(sys.argv[1]) if len(sys.argv) > 1 else 712
OUT = sys.argv[2] if len(sys.argv) > 2 else "/tmp/fp-card.json"
cfg = {"basename": "artificial_lift", "synthetic_card": {"mode": MODE, "seed": SEED},
    "well": {"api14": f"SIM-{MODE}-{SEED}", "rod": {"diameter": 1.0, "length": 5000.0},
        "pump": {"diameter": 1.75, "depth": 5000.0},
        "surface_unit": {"manufacturer": "Sim", "unit_type": "Test", "stroke_length": 144.0, "gear_box_rating": 640000.0},
        "spm": 10.0}, "report": {"html": False}}
wf = DynacardWorkflow(); out_cfg = wf.router(cfg); results = out_cfg["results"]
sc = cfg["well_data"]["surface_card"]
summary = {"mode": MODE, "seed": SEED, "api14": cfg["well_data"]["api14"],
    "position": sc["position"], "load": sc["load"], "n_points": len(sc["position"]),
    "fillage": results.get("pump_fillage"), "buckling_detected": results.get("buckling_detected"),
    "diagnostic_message": results.get("diagnostic_message")}
json.dump(summary, open(OUT, "w"), indent=2)
print("MODE:", MODE, "seed", SEED, "fillage", summary["fillage"], "buckling", summary["buckling_detected"])
print("diag:", summary["diagnostic_message"])
print("written:", OUT)
