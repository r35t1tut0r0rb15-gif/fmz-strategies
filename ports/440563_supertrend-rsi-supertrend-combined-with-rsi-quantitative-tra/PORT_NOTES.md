# #440563 Supertrend结合RSI的量化交易策略Supertrend-Combined-with-RSI-Quantitative-Trading-Strategy -> `fmz_440563_supertrend_flip_rsi72_exit_long`

- FMZ source id: 440563 (lineage).
- Source: https://www.fmz.com/strategy/440563 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-01-31 17:19:28). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C137). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Supertrend direction and RSI |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`factor` [3.0, 2.0] x `exit_long` [72, 80]: **4 trials**; ATR 10 and RSI 14 fixed.

## Ambiguities resolved

- Long only (short entries off by default). FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "supertrend"`.

## Marks

`none`
