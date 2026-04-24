# Native tests

Host-compiled GoogleTest suite. Runs on your laptop, no hardware required.

```bash
pio test -e native
```

Each test folder is a separate binary. Use the fakes in
`components/adapters_fake/` rather than hitting real drivers. Core logic
that depends on hardware should be refactored to accept a port, then
driven here with a fake.

Pyramid: this is **tier 1**. Default every new behaviour to here.
See `docs/testing-strategy.md` for tier selection rules.
