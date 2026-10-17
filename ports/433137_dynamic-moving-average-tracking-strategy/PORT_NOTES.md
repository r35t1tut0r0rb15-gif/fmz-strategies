# #433137 Dynamic Moving Average Tracking Strategy -> `fmz_433137_ut_bot_open_hma`

- FMZ source id: 433137 (lineage).
- Source: https://www.fmz.com/strategy/433137 (PineScript v5, author ChaoZhang, FMZ last
  modified 2023-11-24 16:59:25). Verbatim here as `original_source.md`. Read 2026-10-17 (FMZ-C).
- Status: PORTED (batch C59). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | An ATR trailing line and an average cross |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | The open-profit close-outs and 100 % of equity stored in original_sizing.txt. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`sens` [1.0, 2.0] x `atr_len` [11, 22]: **4 trials**; HMA 2 of the open fixed.

## Ambiguities resolved

- Open-profit close-outs dropped (sizing). Long only. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "volatility_stop_cross"`.

## Marks

`none`
