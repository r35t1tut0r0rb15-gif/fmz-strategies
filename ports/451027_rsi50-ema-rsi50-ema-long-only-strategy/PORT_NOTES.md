# #451027 RSI50_EMA长仓策略-RSI50_EMA-Long-Only-Strategy -> `fmz_451027_sma2_atr_band_breakout_long`

- FMZ source id: 451027 (lineage).
- Source: https://www.fmz.com/strategy/451027 (PineScript v4, author ChaoZhang, FMZ last
  modified 2024-05-11 11:49:29). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C183). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | ATR-band breakouts of a smoothed price |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | The 100 % of equity size stored. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`length` [11, 20] x `mult` [2.0, 1.0]: **4 trials**; the SMA 2 fixed.

## Ambiguities resolved

- RSI block never acts. Long only. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "volatility_channel_breakout"`.

## Marks

`none`
