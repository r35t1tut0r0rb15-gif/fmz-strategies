# #429575 多Bar同向策略Multi-Bar-Direction-Strategy -> `fmz_429575_streak_odds_one_bar`

- FMZ source id: 429575 (lineage).
- Source: https://www.fmz.com/strategy/429575 (PineScript v4, author ChaoZhang, FMZ last
  modified 2023-10-18 12:20:59). Verbatim here as `original_source.md`. Read 2026-10-16 (FMZ-C).
- Status: PORTED (batch C28). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; one-bar holds as exit signals. |
| 2 | PASS | Candle colours and frequencies only. |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | Pyramiding 15 stored. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`threshold` [50.0, 40.0]: **2 trials**; streak length 2 -> 3 (the rule the default settings use).

## Ambiguities resolved

- Only the 2 -> 3 rule acts (ternary precedence). One-bar holds. REVERSAL INTENDED. FREQ = "5min".

## FAMILY (proposed, user to confirm)

`FAMILY = "candle_pattern"`.

## Marks

`none`
