# #427188 Multi-Timeframe Heiken Ashi Crossover Strategy -> `fmz_427188_heikin_ashi_d_w_m`

- FMZ source id: 427188 (lineage).
- Source: https://www.fmz.com/strategy/427188 (PineScript v4, author ChaoZhang, FMZ last
  modified 2023-09-18 21:50:05). Verbatim here as `original_source.md`. Read 2026-10-15 (FMZ-C).
- Status: PORTED (batch C2). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; weekly / monthly values only once those periods have completed. |
| 2 | PASS | Candle colours only. |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`short_on` [False, True]: **2 trials**; default False (the input default). The backtest header's `args` switch shorts on; the grid covers both.

## Ambiguities resolved

- Daily bars are broker days (17:00 New York), stamped with their first minute (house `build_bars` convention).
- Pine v4 `security` defaults to lookahead_off: on history only completed higher bars are used. Under the house rule (skill section 4) a week / month counts as completed from the first daily bar of the next one, one daily bar later than TradingView shows it.
- Weeks are ISO weeks of the broker-day date; months are calendar months of the broker-day date.
- Heikin-Ashi seeded with (open + close) / 2 on each series' first bar.
- FREQ = "1D" from the backtest header.

## FAMILY (proposed, user to confirm)

`FAMILY = "heikin_ashi_trend"`.

## Marks

`none`
