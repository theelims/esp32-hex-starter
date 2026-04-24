# Target (on-chip) tests

Unity tests that flash to the ESP32-S3 and run on the board.

```bash
pio test -e test_esp32s3
```

Pyramid: this is **tier 3**. Only use when behaviour genuinely requires
on-chip execution — ISRs, DMA, FreeRTOS scheduling, flash/NVS, sleep/wake,
or hardware-clocked timing. Everything else goes in `test/native/`.

See `docs/testing-strategy.md` for the full pyramid.
