# #440505 Trend Trading Strategy Based on Price Channel of Double Moving Averages -> `fmz_440505_pac_ema_trend_start_bracket`

- FMZ source id: 440505 (lineage).
- Source: https://www.fmz.com/strategy/440505 (PineScript v4, author ChaoZhang, FMZ last
  modified 2024-01-31 10:37:13). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C135). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; bracket fixed at entry |
| 2 | ADAPT | Tick bracket from the close -> fixed fractions |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`tp` [0.0032, 0.01] x `sl` [0.001, 0.005]: **4 trials**; EMA and PAC lengths and the window fixed.

## Ambiguities resolved

- Tick bracket as fixed fractions; window on the UTC bar open. Entries only from flat. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_trend"`.

## Marks

`none`
