# #458056 Multi Indicator Adaptive Trend Following Strategy -> `fmz_458056_ut_bot_rsi_donchian_band_exit_reversal`

- FMZ source id: 458056 (lineage).
- Source: https://www.fmz.com/strategy/458056 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-07-29 15:51:54). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C200). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; the target / stop exits as close tests |
| 2 | PASS | UT Bot crossings with RSI and Donchian filters |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | ND457811. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`key` [1.0, 2.0] x `dc_len` [20, 50] x `band_pct` [0.002, 0.01]: **8 trials**; the ATR 10 and RSI 14 / 50 fixed.

## Ambiguities resolved

- Exits as close tests. REVERSAL INTENDED. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "atr_trailing_line"`.

## Marks

`none`
