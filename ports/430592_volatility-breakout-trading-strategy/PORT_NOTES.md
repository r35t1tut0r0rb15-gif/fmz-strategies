# #430592 Volatility Breakout Trading Strategy -> `fmz_430592_volatility_breakout_atr`

- FMZ source id: 430592 (lineage).
- Source: https://www.fmz.com/strategy/430592 (PineScript v5, author ChaoZhang, FMZ last
  modified 2023-10-30 16:58:03). Verbatim here as `original_source.md`. Read 2026-10-16 (FMZ-C).
- Status: PORTED (batch C37). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders. |
| 2 | PASS | ATR bands. |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`length` [20, 10, 40]: **3 trials**.

## Ambiguities resolved

- REVERSAL INTENDED. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "atr_band_breakout"`.

## Marks

`none`
