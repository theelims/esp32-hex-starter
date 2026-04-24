# HIL bench (tier 4)

Hardware-in-the-loop tests against the real board, a Siglent SDS1104X-E scope
(LAN/SCPI), and a Nordic PPK2. Marked with `@pytest.mark.hil`; skipped by
default.

## Environment

```bash
export SCOPE_ADDR="TCPIP::<scope-ip>::INSTR"
export PPK2_PORT="/dev/ttyACM1"
export DUT_PORT="/dev/ttyACM0"
```

## Run

```bash
uv run pytest -m hil                         # all HIL tests
uv run pytest -m hil tools/hil/tests/test_bench_smoke.py -v
```

## Scope

Use HIL only for tests that genuinely need it:
- Electrical behaviour — rise time, overshoot, settling.
- Power — deep-sleep µA, wake budgets, inrush.
- End-to-end protocol against a real sensor.

Everything else goes in `test/native/` or `tools/sim/tests/`.
