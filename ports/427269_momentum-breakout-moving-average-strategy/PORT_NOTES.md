# #427269 Momentum Breakout Moving Average Strategy -> `fmz_427269_mbit_ma_count_fade`

- FMZ source id: 427269 (lineage).
- Source: https://www.fmz.com/strategy/427269 (PineScript, no @version line, v5 syntax; author ChaoZhang, FMZ last
  modified 2023-09-19 16:33:13). Verbatim here as `original_source.md`. Read 2026-10-15 (FMZ-C).
- Status: PORTED (batch C3). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders. |
| 2 | PASS | Bar counts only. |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`length` [520, 260, 1040] x `confirm_bars` [27, 13]: **6 trials**; defaults 520 / 27 (the source's).

## Ambiguities resolved

- Contrarian as written: 27 closes below the average buy, 27 above sell (exactly the 27th, `==`).
- REVERSAL INTENDED. FREQ = "5min" from the backtest header.

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_trend"`.

## Marks

`none`
