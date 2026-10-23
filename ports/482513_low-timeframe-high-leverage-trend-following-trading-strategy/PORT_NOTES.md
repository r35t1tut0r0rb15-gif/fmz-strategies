# #482513 Low Timeframe High Leverage Trend Following Trading Strategy -> `fmz_482513_close_ema9_cross_rsi_volume_spike_1_3pct_rr2_1h_reversal`

- FMZ source id: 482513 (lineage).
- Source: https://www.fmz.com/strategy/482513 (PineScript v5, author ChaoZhang, FMZ last
  modified 2025-02-18 18:20:06). Verbatim here as `original_source.md`. Read 2026-10-23 (FMZ-C).
- Status: PORTED (batch V39). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; percent bracket at the signal close as fractions of the fill |
| 2 | PASS | EMA 9 crossings with RSI and volume-spike filters |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code (leverage named in the title only). |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`sl` [0.013, 0.02] x `rr` [2.0, 1.5]: **4 trials**; EMA 9, RSI 14, volume SMA 50 x 1.5.

## Ambiguities resolved

- Bracket at the signal close. Volume = broker tick volume. REVERSAL INTENDED. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_cross"`.

## Marks

`none`
