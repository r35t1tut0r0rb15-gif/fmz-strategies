# #458200 Multi Order Breakout Trend Following Strategy -> `fmz_458200_bb_breakout_sar_ema100_atr_rising_signal_count_long`

- FMZ source id: 458200 (lineage).
- Source: https://www.fmz.com/strategy/458200 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-07-30 17:18:11). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C203). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; the fill-price stop as a fixed fraction |
| 2 | PASS | Band breakouts with trend and volatility filters |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | Equity-risk quantity stored, not ported. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`lookback` [20, 50] x `breakout_mult` [2.0, 1.5] x `sl_pct` [0.02, 0.04]: **8 trials**; the SAR, EMA 100 and the 5-signal limit fixed.

## Ambiguities resolved

- Entries only from flat (pyramiding 1); stop from the fill bar. Long only. FREQ = "3h".

## FAMILY (proposed, user to confirm)

`FAMILY = "bollinger_breakout"`.

## Marks

`coarse_bar_stop`
