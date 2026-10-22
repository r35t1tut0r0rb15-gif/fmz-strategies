# #442117 Momentum Trend Synergy Strategy -> `fmz_442117_rmi_sma5_side_reversal`

- FMZ source id: 442117 (lineage).
- Source: https://www.fmz.com/strategy/442117 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-02-19 14:48:37). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C151). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | REVIEW | RMI and SMA side; the moving stop is pending |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`length_rmi` [21, 14] x `length_st` [5, 10]: **4 trials**; RMI levels 60 / 40 fixed; the stop is pending.

## Ambiguities resolved

- The re-sent SMA -+ 4 ATR stop is pending (trailing_stop_pending). REVERSAL INTENDED. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "rsi_oscillator"`.

## Marks

`trailing_stop_pending`
