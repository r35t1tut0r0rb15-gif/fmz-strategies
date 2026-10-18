# #436599 连续N根K线收阴策略N-Bar-Close-Below-Open-Short-Strategy -> `fmz_436599_n_bars_down_short`

- FMZ source id: 436599 (lineage).
- Source: https://www.fmz.com/strategy/436599 (PineScript v4, author ChaoZhang, FMZ last
  modified 2023-12-26 10:29:12). Verbatim here as `original_source.md`. Read 2026-10-18 (FMZ-C).
- Status: PORTED (batch C92). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | ADAPT | Price-unit levels -> fractions of the reference close |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | The take profit and stop inputs stored. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | ND434674. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`n_length` [4, 3] x `tp_frac` [0.0018, 0.005]: **4 trials**; the stop is half the target.

## Ambiguities resolved

- Price-unit levels re-expressed as fractions; exit one bar after the touch. Short only. FREQ = "30min".

## FAMILY (proposed, user to confirm)

`FAMILY = "candle_pattern"`.

## Marks

`none`
