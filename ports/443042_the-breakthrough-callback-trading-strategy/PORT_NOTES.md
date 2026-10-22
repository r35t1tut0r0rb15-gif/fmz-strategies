# #443042 The Breakthrough Callback Trading Strategy -> `fmz_443042_cumulative_strength_macd_ema_stack_reversal`

- FMZ source id: 443042 (lineage).
- Source: https://www.fmz.com/strategy/443042 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-02-28 18:01:56). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C165). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Cumulative strength with an MACD / EMA filter |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | The commission stored. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`fast_length` [23, 12] x `slow_length` [11, 26]: **4 trials**; the EMAs and the strength average fixed.

## Ambiguities resolved

- Cumulative sums from the data start; MACD lengths as written. REVERSAL INTENDED. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "momentum_oscillator"`.

## Marks

`none`
