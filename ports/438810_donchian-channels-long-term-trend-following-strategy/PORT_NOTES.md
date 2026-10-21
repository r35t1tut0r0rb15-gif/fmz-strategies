# #438810 Donchian Channels Long Term Trend Following Strategy -> `fmz_438810_donchian_breakout_middle_exit`

- FMZ source id: 438810 (lineage).
- Source: https://www.fmz.com/strategy/438810 (PineScript v4, author ChaoZhang, FMZ last
  modified 2024-01-15 14:48:03). Verbatim here as `original_source.md`. Read 2026-10-21 (FMZ-C).
- Status: PORTED (batch C113). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Donchian bands of past bars |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`length` [20, 55] x `double_mid` [True, False]: **4 trials**.

## Ambiguities resolved

- Past-bar bands; reversal stands on entry bars. REVERSAL INTENDED. FREQ = "15min".

## FAMILY (proposed, user to confirm)

`FAMILY = "donchian_breakout"`.

## Marks

`none`
