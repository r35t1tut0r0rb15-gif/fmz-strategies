# #473669 Multi Technical Indicator Trend Following Trading Strategy -> `fmz_473669_rsi50_cross_engulf_volume_sma200_no_exit_long_only`

- FMZ source id: 473669 (lineage).
- Source: https://www.fmz.com/strategy/473669 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-12-02 10:40:02). Verbatim here as `original_source.md`. Read 2026-10-23 (FMZ-C).
- Status: PORTED (batch V34). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | RSI 50 crossings in an uptrend on volume and engulfing candles |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`fast` [14, 20] x `slow` [200, 100]: **4 trials**; RSI 14, volume SMA 20.

## Ambiguities resolved

- No exit: one long held to the end of the data. Volume = broker tick volume. Long only. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "rsi_momentum"`.

## Marks

`none`
