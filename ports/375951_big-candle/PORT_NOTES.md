# #375951 Big-candle分享 -> `fmz_375951_big_candle_volume_ema50_adx_supertrend_pct_bracket_reversal`

- FMZ source id: 375951 (lineage).
- Source: https://www.fmz.com/strategy/375951 (PineScript v5, author a624587332, FMZ last
  modified 2022-08-02 14:31:12). Verbatim here as `original_source.md`. Read 2026-10-23 (FMZ-C).
- Status: PORTED (batch V3). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; percent bracket from the fill |
| 2 | PASS | Volume-confirmed big candles with trend filters |
| 3 | PASS | No exchange header. |
| 4 | DONE | 100 % of equity, capital 10000 and commission 0.04 % stored, not ported. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`multiplier` [1.8, 1.5] x `lookback` [120, 60]: **4 trials**; EMA 50, DMI 7 / 26, SuperTrend 2 / 10, TP 1.3 %, SL 9 %.

## Ambiguities resolved

- Every bull / bear bar enters (the flag is set first), as written. Window dropped. Volume = broker tick volume.
- REVERSAL INTENDED. FREQ = "bar_size_pending".

## FAMILY (proposed, user to confirm)

`FAMILY = "candle_pattern"`.

## Marks

`bar_size_pending`
