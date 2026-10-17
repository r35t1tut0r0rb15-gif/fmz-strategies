# #434486 趋势ATR横向突破策略Honey-Trend-ATR-Breakout-Strategy -> `fmz_434486_daily_pivot_atr_band_dti`

- FMZ source id: 434486 (lineage).
- Source: https://www.fmz.com/strategy/434486 (PineScript v2, author ChaoZhang, FMZ last
  modified 2023-12-06 18:03:38). Verbatim here as `original_source.md`. Read 2026-10-17 (FMZ-C).
- Status: PORTED (batch C68). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; stop fixed at entry |
| 2 | ADAPT | Tick stop -> ATR multiple; pivot bands from prior broker days |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | The fixed quantity 1 and the capital stored. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | ND434486. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`atrdiv` [2.0, 1.0] x `sl_atr` [0.05, 1.0]: **4 trials**; ATR 13, the DTI periods and ATR 3 / 50 fixed.

## Ambiguities resolved

- Prior broker day's pivot and ATR; tick stop -> 0.05 ATR. Flat tracked through the stop and the exits. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "pivot_reversal"`.

## Marks

`none`
