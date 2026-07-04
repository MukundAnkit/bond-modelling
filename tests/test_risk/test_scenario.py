import numpy as np

from src.risk.scenario import ScenarioGenerator


class DummyCurve:
    def __init__(self, tenors, yields):
        self.tenors = np.array(tenors)
        self.yields = np.array(yields)


def test_non_parallel_steepening():
    base_curve = DummyCurve(tenors=[1, 2, 5, 10], yields=[0.02, 0.025, 0.03, 0.04])
    generator = ScenarioGenerator()

    # Apply steepening shift
    shocked_curve = generator.apply_non_parallel_shift(
        base_curve, shift_type="steepening", alpha=0.01
    )

    # Long term yield should increase more than short term
    short_diff = shocked_curve.yields[0] - base_curve.yields[0]
    long_diff = shocked_curve.yields[-1] - base_curve.yields[-1]
    assert long_diff > short_diff
    assert shocked_curve.yields[-1] > 0.04


def test_non_parallel_flattening():
    base_curve = DummyCurve(tenors=[1, 2, 5, 10], yields=[0.02, 0.025, 0.03, 0.04])
    generator = ScenarioGenerator()

    shocked_curve = generator.apply_non_parallel_shift(
        base_curve, shift_type="flattening", alpha=0.01
    )

    # Long term yield should decrease more than short term
    short_diff = shocked_curve.yields[0] - base_curve.yields[0]
    long_diff = shocked_curve.yields[-1] - base_curve.yields[-1]
    assert long_diff < short_diff


def test_non_parallel_twist():
    base_curve = DummyCurve(tenors=[1, 2, 5, 10], yields=[0.02, 0.025, 0.03, 0.04])
    generator = ScenarioGenerator()

    # Pivot at 5 years (index 2)
    shocked_curve = generator.apply_non_parallel_shift(
        base_curve, shift_type="twist", alpha=0.01, pivot=5
    )

    # Yield at pivot should remain roughly unchanged
    np.testing.assert_almost_equal(
        shocked_curve.yields[2], base_curve.yields[2], decimal=4
    )
    # Short term should change in opposite direction to long term
    assert np.sign(shocked_curve.yields[0] - base_curve.yields[0]) != np.sign(
        shocked_curve.yields[-1] - base_curve.yields[-1]
    )


def test_policy_shock_decay():
    base_curve = DummyCurve(tenors=[1, 2, 5, 10], yields=[0.02, 0.025, 0.03, 0.04])
    generator = ScenarioGenerator()

    # 50 bps shock at short end
    shocked_curve = generator.apply_policy_shock(base_curve, delta_r=0.005, decay=0.5)

    # Short term yield should increase by close to 50 bps
    # Long term yield should increase by much less
    short_diff = shocked_curve.yields[0] - base_curve.yields[0]
    long_diff = shocked_curve.yields[-1] - base_curve.yields[-1]

    assert short_diff > 0.002  # at least some shock
    assert long_diff < short_diff  # decay effect
