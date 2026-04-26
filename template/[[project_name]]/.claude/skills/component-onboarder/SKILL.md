---
name: component-onboarder
description: Ingests a chip datasheet PDF and produces a datasheet.md extract, register_map.md, a regs.hpp header, and a per-chip skill. Invoke when a new chip is added to the board.
trigger: /component-onboarder
tools: Read, Write, Edit, Glob, Grep, Bash, WebSearch, WebFetch
model: opus
---

# /component-onboarder

You onboard a new chip into the project. Inputs the user gives you:

- The chip name (e.g. `LSM6DSO`).
- A datasheet PDF at `hardware/datasheets/<chip>/datasheet.pdf`.

Execute in this order. Do not skip steps.

## 1. Read the datasheet
Use Read on the PDF. Extract only the sections that matter for firmware:
- Register map (full — every address, reset value, and field).
- Functional descriptions of operating modes and state machines.
- Communication protocol (I2C/SPI framing, command set).
- Interrupt behaviour and signals.
- Electrical characteristics relevant to timing and power modes.

Skip: mechanical drawings, package dimensions, ordering info, revision history, marketing overview.

## 2. Write `datasheet.md`
Path: `hardware/datasheets/<chip>/datasheet.md`.
Structure with `##` headings for each kept section. Preserve tables as markdown tables. Include page-number references back to the PDF for anything you compressed or paraphrased.

## 3. Write `register_map.md`
Path: `hardware/datasheets/<chip>/register_map.md`.
One table per register group. Columns: `| Addr | Name | Reset | Access | Fields | Notes |`.
Fields are expanded as a sub-list when non-trivial.

## 4. Generate `<chip>_regs.hpp`
Path: `components/drivers/<chip>/include/<chip>_regs.hpp`.
Use `constexpr uint8_t` for addresses, `constexpr uint8_t` for bit masks, and enums where the datasheet defines named values. Do not invent names — transcribe the datasheet's.

## 5. Find reference implementations
Do a GitHub search for drivers targeting this chip. Collect 3–5 links, prioritizing in this order:
  1. Official vendor SDK / reference driver.
  2. SparkFun Arduino library.
  3. Adafruit Arduino library.
  4. High-quality embedded-hal / ESP-IDF community drivers.
  5. Zephyr upstream driver, if one exists.

Do not link low-quality forks or machine-generated libraries.

## 6. Write the skill
Path: `.claude/skills/<chip>-driver/SKILL.md`.
Structure:

~~~
---
name: <chip>-driver
description: Working with the <CHIP>. Protocol, register map, known patterns, reference libraries. Use this skill when writing, reviewing, or debugging driver code for <CHIP>.
---

# <CHIP> driver guide

## Protocol
<one paragraph: I2C/SPI, mode, max speed, framing quirks>

## Key registers
<the 5–10 registers you actually touch most, with a sentence each>
(For the full map, see ../../hardware/datasheets/<chip>/register_map.md)

## Known-good driver template
<50–100 lines of C++17, talks to II2cBus or ISpiBus port, returns
Result<T, Error>. Must be copy-pasteable and work with the project's
fakes for unit testing.>

## Reference implementations
1. <official-sdk-link> — <one-line description>
2. <sparkfun-link> — <one-line description>
3. ...

## Gotchas
<things that only show up after you've worked with this chip>
~~~

## 7. Report back
Summarise to the user:
- Pages you kept vs skipped in datasheet.md.
- Count of registers in register_map.md.
- Reference libraries found.
- Anything the datasheet was ambiguous about (flag for human review).

Stop after reporting. Do not write a driver — the `driver-author` sub-agent does that in a separate invocation, using your outputs.
