# #440312 Triple Indicator Collision Strategy -> `fmz_440312_ema_macd_rsi_agreement`

- FMZ source id: 440312 (lineage).
- Source: https://www.fmz.com/strategy/440312 (PineScript v4, author ChaoZhang, FMZ last
  modified 2024-01-29 11:24:11). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C132). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | EMA, MACD and RSI levels |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`ema_len` [20, 50] x `signal_len` [20, 9]: **4 trials**; the same signal length for the MACD and the RSI; MACD 12 / 26 and RSI 14 fixed.

## Ambiguities resolved

- REVERSAL INTENDED. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "multi_indicator_confluence"`.

## Marks

`none`
