# Python device simulation (tier 2)

Runs the C++ core against richer device scenarios than the C++ fakes cover
well: recorded IMU traces, multi-device bus choreography, fault injection.

```bash
uv run pytest tools/sim/tests
```

The default C++ fakes in `components/adapters_fake/` are the primary tool;
reach for this layer only when expressing the scenario in C++ is painful.

See `docs/testing-strategy.md` for the tier-2 rules.
