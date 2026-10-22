# #454150 Moving Average Crossover Strategy -> `fmz_454150_sma9_21_cross_5m_reversal`

- FMZ source id: 454150 (lineage).
- Source: https://www.fmz.com/strategy/454150 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-06-14 15:48:32). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C194). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | SMA crossings |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | The range-based quantity stored. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`fast` [9, 5] x `slow` [21, 50]: **4 trials**.

## Ambiguities resolved

- REVERSAL INTENDED. FREQ = "5min".

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_cross"`.

## Marks

`none`
