# Cantilever Beam — Tip Deflection Under a Point Load

A cantilever beam is fixed (clamped) at one end and free at the other. When a
point load `P` is applied at the free end, the downward deflection at that tip
is:

```
δ = P · L³ / (3 · E · I)
```

where:

| Symbol | Quantity                  | Units |
|--------|---------------------------|-------|
| δ      | Tip deflection            | m     |
| P      | Point load at free end    | N     |
| L      | Beam length               | m     |
| E      | Young's modulus           | Pa    |
| I      | Second moment of area     | m⁴    |

## Worked example

A horizontal structural-steel cantilever:

- `P = 5000 N` (point load at the free end)
- `L = 2.0 m`
- `E = 200 × 10⁹ Pa` (200 GPa, typical for steel)
- `I = 8.0 × 10⁻⁶ m⁴`

```
δ = (5000 · 2.0³) / (3 · 200e9 · 8.0e-6)
  = 40000 / 4.8e6
  = 8.33 × 10⁻³ m
  ≈ 8.33 mm
```

So the free end deflects about **8.33 mm** under the load.

## Assumptions

- Linear-elastic material (Hooke's law holds; no yielding).
- Small deflections (δ ≪ L), so geometry is treated as undeformed.
- Euler–Bernoulli beam theory (plane sections stay plane; shear deformation
  neglected — valid for slender beams).
- Prismatic beam (constant `E` and `I` along its length).

---

This is an illustrative, open example for learning and demonstration — verify
against your own governing code and engineering judgement before any real use.
