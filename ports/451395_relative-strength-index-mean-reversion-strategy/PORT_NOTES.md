# #451395 Relative Strength Index Mean Reversion Strategy -> `fmz_451395_rsi_extreme_beyond_sma20_reversal`

- FMZ source id: 451395 (lineage).
- Source: https://www.fmz.com/strategy/451395 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-05-14 16:01:29). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C184). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | RSI extremes beyond the SMA |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`rsi_len` [14, 7] x `sma_len` [20, 50]: **4 trials**; the levels fixed.

## Ambiguities resolved

- The close names a never-entered id. REVERSAL INTENDED. FREQ = "3h".

## FAMILY (proposed, user to confirm)

`FAMILY = "rsi_oscillator"`.

## Marks

`none`
