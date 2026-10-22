# #442551 The Oscillating Breakthrough Strategy -> `fmz_442551_rsi_dip_sma170_trend_pct_stop_long`

- FMZ source id: 442551 (lineage).
- Source: https://www.fmz.com/strategy/442551 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-02-22 17:15:01). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C158). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; stop fixed from the fill |
| 2 | PASS | RSI dip with an SMA trend filter; SMA cross exit |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | The percent-of-equity size, capital and commission stored. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`over_sold` [40, 30] x `sl_pct` [0.05, 0.03]: **4 trials**; the SMA and RSI lengths fixed.

## Ambiguities resolved

- Stop from the fill bar as a fixed fraction. Long only. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "rsi_oscillator"`.

## Marks

`none`
