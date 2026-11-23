"""Tip deflection of a cantilever beam under a point load at the free end.

Euler-Bernoulli, linear-elastic, small-deflection assumptions:

    delta = P * L**3 / (3 * E * I)

Dependency-free. Run with:  python3 deflection.py
"""


def tip_deflection_point_load(load, length, youngs_modulus, second_moment):
    """Return cantilever tip deflection (m) for a free-end point load.

    Args:
        load:           Point load P at the free end (N).
        length:         Beam length L (m).
        youngs_modulus: Young's modulus E (Pa).
        second_moment:  Second moment of area I (m**4).
    """
    return load * length**3 / (3.0 * youngs_modulus * second_moment)


if __name__ == "__main__":
    # Structural-steel cantilever worked example.
    P = 5000.0      # N
    L = 2.0         # m
    E = 200.0e9     # Pa (200 GPa)
    I = 8.0e-6      # m**4

    delta = tip_deflection_point_load(P, L, E, I)
    print("Cantilever tip deflection under a free-end point load")
    print(f"  P = {P:.0f} N, L = {L:.1f} m, E = {E:.3g} Pa, I = {I:.3g} m^4")
    print(f"  delta = {delta:.6e} m = {delta * 1000.0:.3f} mm")
