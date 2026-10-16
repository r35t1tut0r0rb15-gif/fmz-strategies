# #430152 Double Moving Average Crossover Strategy -> `fmz_430152_delayed_ema_state_cross`

- FMZ source id: 430152 (lineage).
- Source: https://www.fmz.com/strategy/430152 (PineScript v4, author ChaoZhang, FMZ last
  modified 2023-10-25 15:14:35). Verbatim here as `original_source.md`. Read 2026-10-16 (FMZ-C).
- Status: PORTED (batch C33). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders. |
| 2 | PASS | Moving-average states. |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`delay` [10, 5] x `slow` [50, 100]: **4 trials**; EMA 20 fixed, the second look-back is delay + 1.

## Ambiguities resolved

- The crosswise close conditions are ported as written (positions of about one bar). REVERSAL INTENDED. FREQ = "2h".

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_cross"`.

## Marks

`none`
