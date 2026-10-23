# #430261 Volatility Force Breakthrough Trading Strategy -> `fmz_430261_cumulative_force_ema3_20_rising_atr_reversal`

- FMZ source id: 430261 (lineage).
- Source: https://www.fmz.com/strategy/430261 (PineScript v2, author ChaoZhang, FMZ last
  modified 2023-10-26 16:17:17). Verbatim here as `original_source.md`. Read 2026-10-23 (FMZ-C).
- Status: PORTED (batch V10). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Cumulative force EMA cross in rising volatility |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`fast` [3, 5] x `slow` [20, 50]: **4 trials**; ATR 20 / 50.

## Ambiguities resolved

- Volume = broker tick volume. REVERSAL INTENDED. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "force_index"`.

## Marks

`none`
