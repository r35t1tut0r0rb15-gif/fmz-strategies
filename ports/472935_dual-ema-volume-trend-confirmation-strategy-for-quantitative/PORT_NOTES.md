# #472935 Dual EMA Volume Trend Confirmation Strategy for Quantitative Trading -> `fmz_472935_ema21_50_cross_volume_ema_exit_reversal`

- FMZ source id: 472935 (lineage).
- Source: https://www.fmz.com/strategy/472935 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-11-25 11:07:03). Verbatim here as `original_source.md`. Read 2026-10-23 (FMZ-C).
- Status: PORTED (batch V33). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | EMA 21 / 50 crossings with volume filters and EMA exits |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`fast` [21, 13] x `slow` [50, 34]: **4 trials**; volume SMA 20.

## Ambiguities resolved

- Short needs low volume (as written). Volume = broker tick volume. REVERSAL INTENDED. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_cross"`.

## Marks

`none`
