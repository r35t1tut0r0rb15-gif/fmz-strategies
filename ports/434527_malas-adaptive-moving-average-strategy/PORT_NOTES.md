# #434527 Malas Adaptive Moving Average Strategy -> `fmz_434527_mesa_mama_fama_side`

- FMZ source id: 434527 (lineage).
- Source: https://www.fmz.com/strategy/434527 (PineScript v4, author ChaoZhang, FMZ last
  modified 2023-12-07 11:08:18). Verbatim here as `original_source.md`. Read 2026-10-17 (FMZ-C).
- Status: PORTED (batch C68). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Adaptive averages of hl2 |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`fast_limit` [0.5, 0.25] x `slow_limit` [0.05, 0.02]: **4 trials**.

## Ambiguities resolved

- Author's transcription kept (Im sign, per-bar resets). REVERSAL INTENDED. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_trend"`.

## Marks

`none`
