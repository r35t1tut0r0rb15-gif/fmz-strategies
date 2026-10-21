# #437786 Moving Average System Trading Strategy -> `fmz_437786_ma17_side_change`

- FMZ source id: 437786 (lineage).
- Source: https://www.fmz.com/strategy/437786 (PineScript v4, author ChaoZhang, FMZ last
  modified 2024-01-05 15:36:00). Verbatim here as `original_source.md`. Read 2026-10-21 (FMZ-C).
- Status: PORTED (batch C106). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Close sides of a moving average |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | The capital, percent-of-equity size and commission stored. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`length` [17, 34] x `ma_type` ["sma", "ema"]: **4 trials**; source ohlc4 fixed.

## Ambiguities resolved

- Side-change crossovers of the last-bar stamps; MA type swept over sma / ema. REVERSAL INTENDED. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_trend"`.

## Marks

`none`
