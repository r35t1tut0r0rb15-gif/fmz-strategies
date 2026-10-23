# #440813 Double Exponential Moving Average Quant Trading Strategy -> `fmz_440813_ema5_sma20_cross_tii_band_exit_2h_long_only`

- FMZ source id: 440813 (lineage).
- Source: https://www.fmz.com/strategy/440813 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-02-02 11:41:34). Verbatim here as `original_source.md`. Read 2026-10-23 (FMZ-C).
- Status: PORTED (batch V25). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; close-based +-5 % exit in the signals |
| 2 | PASS | EMA / SMA crossings filtered by the trend intensity index |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`major` [60, 30] x `band` [0.05, 0.03]: **4 trials**; minor 30, EMA 5 / SMA 20.

## Ambiguities resolved

- Reference resets on every buy signal. Volume not used. Long only. FREQ = "2h".

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_cross"`.

## Marks

`none`
