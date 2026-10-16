# #430280 Cryptocurrency动量突破策略Cryptocurrency-Momentum-Breakout-Strategy -> `fmz_430280_pump_dump_bodies_long`

- FMZ source id: 430280 (lineage).
- Source: https://www.fmz.com/strategy/430280 (PineScript v3, author ChaoZhang, FMZ last
  modified 2023-10-26 17:23:20). Verbatim here as `original_source.md`. Read 2026-10-16 (FMZ-C).
- Status: PORTED (batch C34). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; close-checked low exit. |
| 2 | PASS | Body ratios. |
| 3 | PASS | "Cryptocurrency" in the corpus title only; exchange pair in the header. |
| 4 | DONE | 100 % of equity per entry stored in original_sizing.txt. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`length` [100, 50] x `multiplier` [3.0, 2.0]: **4 trials**; the inert 100 % stop not ported.

## Ambiguities resolved

- Close-checked low exit (market next open). The 100 % stop is inert. Long only. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "momentum_breakout"`.

## Marks

`none`
