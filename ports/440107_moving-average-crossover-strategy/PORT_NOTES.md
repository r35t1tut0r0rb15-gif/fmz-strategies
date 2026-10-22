# #440107 Moving Average Crossover Strategy -> `fmz_440107_close_vs_daily_close_sma`

- FMZ source id: 440107 (lineage).
- Source: https://www.fmz.com/strategy/440107 (PineScript v4, author ChaoZhang, FMZ last
  modified 2024-01-26 16:29:23). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C131). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; daily values from completed days |
| 2 | PASS | Close against an average of the daily close |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | ND429383. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`length` [14, 50]: **2 trials**; reverse off.

## Ambiguities resolved

- Daily close from the last completed broker day; SMA over 1-hour values. REVERSAL INTENDED. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_trend"`.

## Marks

`none`
