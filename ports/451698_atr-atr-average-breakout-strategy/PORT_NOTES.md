# #451698 ATR均线突破策略-ATR-Average-Breakout-Strategy -> `fmz_451698_sma_atr_band_breakout_band_exits_reversal`

- FMZ source id: 451698 (lineage).
- Source: https://www.fmz.com/strategy/451698 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-05-17 10:22:11). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C186). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | ATR-band breakouts with band exits |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | The risk-per-ATR quantity stored. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`length` [20, 50] x `mult` [2.0, 3.0]: **4 trials**; the exit multiples 1 / 2 fixed.

## Ambiguities resolved

- Call order: a held long closes on the next breakout bar. REVERSAL INTENDED. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "volatility_channel_breakout"`.

## Marks

`none`
