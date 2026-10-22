# #451074 Multi Moving Average Trend Trading Strategy -> `fmz_451074_sma9_cross_above_sma21_200_tick_bracket_long`

- FMZ source id: 451074 (lineage).
- Source: https://www.fmz.com/strategy/451074 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-05-11 17:32:49). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C184). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; bracket fixed from the signal close |
| 2 | PASS | SMA trend pullback crossings with a tick bracket |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code; the tick bracket quoted in original_sizing.txt. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`k_atr` [0.0286, 1.0] x `ma_medium` [21, 50]: **4 trials**; the SMA 9 and SMA 200 fixed.

## Ambiguities resolved

- Tick bracket as 0.0286 ATR(14); close-all never fires. Long only. FREQ = "3h".

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_trend"`.

## Marks

`coarse_bar_stop`
