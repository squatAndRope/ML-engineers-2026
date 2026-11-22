"""Generate the teaching datasets for the welded cantilever bracket.

Simplified analytical model of a parametric strength calculation series:
  nominal bending stress  s_nom = 6 F L / (b t^2)
  stress concentration    Kt    = 1 + 0.3 * sqrt(t / r)
  max stress              s_max = Kt * s_nom  (+ ~1 % "mesh" noise)
  tip deflection          d     = 4 F L^3 / (E b t^3)
  safety factor           SF    = 355 MPa / s_max   (S355 steel)
Fixed: L = 150 mm, b = 40 mm.
"""
import numpy as np
import pandas as pd
from pathlib import Path

rng = np.random.default_rng(42)
OUT = Path(__file__).resolve().parent.parent / "data"
L, B, YIELD = 150.0, 40.0, 355.0
N = 300

t = rng.uniform(8, 20, N).round(1)
r = rng.uniform(1, 8, N).round(1)
F = rng.uniform(200, 3000, N).round(0)
E = rng.uniform(190, 210, N).round(1)          # GPa

s_nom = 6 * F * L / (B * t**2)
kt = 1 + 0.3 * np.sqrt(t / r)
s_max = (kt * s_nom * rng.normal(1, 0.01, N)).round(1)
d = (4 * F * L**3 / (E * 1000 * B * t**3)).round(3)
sf = (YIELD / s_max).round(3)

clean = pd.DataFrame({
    "run_id": [f"R{i:03d}" for i in range(1, N + 1)],
    "thickness_mm": t, "fillet_radius_mm": r, "load_N": F, "E_GPa": E,
    "max_stress_MPa": s_max, "deflection_mm": d, "safety_factor": sf,
})
clean.to_csv(OUT / "bracket.csv", index=False)

# ---- raw version with realistic problems (session 2.5) ----
raw = clean.copy()
raw["solver_status"] = "converged"
raw = raw.astype({"load_N": "object", "max_stress_MPa": "object"})
idx = rng.choice(N, 40, replace=False)
miss_def, miss_E, kn, diverged, typo, txt = idx[:6], idx[6:10], idx[10:16], idx[16:20], idx[20:22], idx[22:25]
raw.loc[miss_def, "deflection_mm"] = np.nan
raw.loc[miss_E, "E_GPa"] = np.nan
raw.loc[kn, "load_N"] = (raw.loc[kn, "load_N"].astype(float) / 1000).round(2)   # entered in kN
raw.loc[diverged, "solver_status"] = "diverged"
raw.loc[diverged, "max_stress_MPa"] = 0.0
raw.loc[diverged, "safety_factor"] = np.nan
raw.loc[typo[0], "thickness_mm"] = -raw.loc[typo[0], "thickness_mm"]
raw.loc[typo[1], "thickness_mm"] = raw.loc[typo[1], "thickness_mm"] * 10
raw.loc[txt, "max_stress_MPa"] = "n/a"
raw = pd.concat([raw, raw.iloc[[5, 77, 150]]], ignore_index=True)      # duplicated runs
raw = raw.sample(frac=1, random_state=1).reset_index(drop=True)
raw.to_csv(OUT / "bracket_raw.csv", index=False, sep=";", decimal=",")

# ---- wide load-case table (session 2.6) ----
sub = clean.iloc[:60]
wide = sub[["run_id", "thickness_mm", "fillet_radius_mm"]].copy()
wide["stress_LC1_static"] = sub["max_stress_MPa"]
wide["stress_LC2_impact"] = (sub["max_stress_MPa"] * 1.4).round(1)
# lateral load case: grows with plate thickness (stiffer plate attracts more load)
wide["stress_LC3_lateral"] = (sub["max_stress_MPa"] * 1.1 * (sub["thickness_mm"] / 12) ** 1.5).round(1)
wide.to_csv(OUT / "bracket_loadcases.csv", index=False)

# ---- materials lookup (merge example) ----
pd.DataFrame({
    "material": ["S235", "S355", "S460"],
    "yield_MPa": [235, 355, 460],
}).to_csv(OUT / "materials.csv", index=False)
print("written to", OUT)
