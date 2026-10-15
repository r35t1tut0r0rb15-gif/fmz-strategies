# #427260 Trend Breakout Strategy Based on Adaptive MA and Trendlines -> `fmz_427260_bannos_trama_trendline_long`

- FMZ source id: 427260 (lineage).
- Source: https://www.fmz.com/strategy/427260 (PineScript v5, author ChaoZhang, FMZ last
  modified 2023-09-19 15:49:37). Verbatim here as `original_source.md`. Read 2026-10-15 (FMZ-C).
- Status: PORTED (batch C3). Not run.
- Near-duplicate group: **DG427260** (with #430051, Jaccard 0.940); ported anyway (rule 7).

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; pivots only once confirmed. |
| 2 | PASS | Bar counts; the 1.0 price-unit slope never acts (see below). |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | DG427260. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`length_trama` [99, 50] x `pivot` [14, 7] x `rsi_exit` [70, 80]: **8 trials**; defaults 99 / 14 / 70 (the source's).

## Ambiguities resolved

- **As the script behaves:** `upper = 0.` / `slope_ph = 0.` are re-declared every bar (no `var`), so `upper` is the pivot high on a confirming bar and 0 otherwise; `crossover(close, upper)` is true exactly on the bar after a pivot high is confirmed. The descending trendline the author evidently intended is not what runs. **Decision owed:** port the intended trendline as a separate module (its 1.0-per-bar slope would become an ATR multiple).
- One entry per UTC calendar month; the month is recorded even when the signal comes while a position is open (Pine).
- Long only. FREQ = "15min" from the backtest header.

## FAMILY (proposed, user to confirm)

`FAMILY = "volatility_channel_breakout"`.

## Marks

`none`
