# #439973 Reversal Trading Strategy Based on Moving Average Range -> `fmz_439973_sma_fan_trap_contrarian`

- FMZ source id: 439973 (lineage).
- Source: https://www.fmz.com/strategy/439973 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-01-25 14:16:28). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C128). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | SMA fans and an SMA side |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`tlenght` [200, 100] x `sslenght` [8, 13]: **4 trials**; SMA 3 / 5 fixed.

## Ambiguities resolved

- Closes after entries. REVERSAL INTENDED. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "mean_reversion"`.

## Marks

`none`
