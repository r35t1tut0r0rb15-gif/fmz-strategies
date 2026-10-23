# #478745 Advanced Multi Indicator Trend Confirmation Trading Strategy -> `fmz_478745_ema50_side_rising_volume_atr_bracket_reversal`

- FMZ source id: 478745 (lineage).
- Source: https://www.fmz.com/strategy/478745 (PineScript v5, author ChaoZhang, FMZ last
  modified 2025-01-17 16:33:07). Verbatim here as `original_source.md`. Read 2026-10-23 (FMZ-C).
- Status: PORTED (batch V37). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; ATR bracket at the signal close as fractions of the fill |
| 2 | PASS | EMA 50 side on rising high volume |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`ema_len` [50, 100] x `vol_mult` [1.5, 2.0]: **4 trials**; ATR 14, SL 2, TP 3.

## Ambiguities resolved

- Repeated signals re-send the bracket (pending). Volume = broker tick volume. REVERSAL INTENDED. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "volume_trend"`.

## Marks

`coarse_bar_stop, trailing_stop_pending`
