# #474836 Multi Moving Average Trading System with Momentum and Volume Confirmation Quantitative Trend Strategy -> `fmz_474836_hull3_vwma3_adx_rsi_volume_state_1h_reversal`

- FMZ source id: 474836 (lineage).
- Source: https://www.fmz.com/strategy/474836 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-12-12 14:27:59). Verbatim here as `original_source.md`. Read 2026-10-23 (FMZ-C).
- Status: PORTED (batch V35). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Fast Hull-style slope with VWMA, ADX, RSI and volume filters |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`keh` [3, 9] x `adx_min` [20.0, 25.0]: **4 trials**; VWMA 3, ADX 14, RSI 14, volume SMA 10.

## Ambiguities resolved

- Script's own ADX (moves not compared). Volume = broker tick volume. REVERSAL INTENDED. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "hull_ma"`.

## Marks

`none`
