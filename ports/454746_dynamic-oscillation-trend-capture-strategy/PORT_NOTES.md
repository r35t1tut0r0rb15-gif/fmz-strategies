# #454746 Dynamic Oscillation Trend Capture Strategy -> `fmz_454746_macd_cross_hilo_activator_reversal`

- FMZ source id: 454746 (lineage).
- Source: https://www.fmz.com/strategy/454746 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-06-21 15:40:25). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C196). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | MACD crossings with a Hilo filter |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`hilo_len` [4, 8] x `fast` [12, 8] x `slow` [26, 21]: **8 trials**; the signal 9 fixed.

## Ambiguities resolved

- valuewhen occurrence 4 as written. REVERSAL INTENDED. FREQ = "3h".

## FAMILY (proposed, user to confirm)

`FAMILY = "macd_cross"`.

## Marks

`none`
