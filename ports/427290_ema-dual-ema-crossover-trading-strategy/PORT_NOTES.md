# #427290 Dual EMA Crossover Trading Strategy -> `fmz_427290_two_ema_gap_trend`

- FMZ source id: 427290 (lineage).
- Source: https://www.fmz.com/strategy/427290 (PineScript v3, author ChaoZhang, FMZ last
  modified 2023-09-19 19:36:03). Verbatim here as `original_source.md`. Read 2026-10-15 (FMZ-C).
- Status: PORTED (batch C4). Not run.
- Near-duplicate group: **DG427290** (with #430132, Jaccard 1.000; the screen did not mark it an exact duplicate); ported anyway (rule 7). When #430132 is read it should be checked for an exact duplicate in behaviour (rule 7, DUPLICATE_ON_READING).

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders. |
| 2 | ADAPT | 0.95 % gap between the EMAs -> `diff_atr` x ATR(14). |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | 100 % of equity, commission stored. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | DG427290. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`diff_atr` [1, 0.5, 2] x `long_ema` [26, 50]: **6 trials**; defaults 1.0 / 26; EMA 13 fixed.

## Ambiguities resolved

- Percent gap re-expressed in ATR (0.95 % on 4-hour BTC bars is about one ATR; judgement before any backtest).
- Opposite entries reverse and win over a same-bar close (REVERSAL INTENDED). FREQ = "4h".

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_trend"`.

## Marks

`none`
