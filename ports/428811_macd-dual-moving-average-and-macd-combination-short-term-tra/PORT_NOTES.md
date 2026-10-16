# #428811 双重均线与MACD组合短线策略Dual-Moving-Average-and-MACD-Combination-Short-term-Trading-Strategy -> `fmz_428811_ema50_scalper_bracket`

- FMZ source id: 428811 (lineage).
- Source: https://www.fmz.com/strategy/428811 (PineScript v4, author ChaoZhang, FMZ last
  modified 2023-10-09 16:47:42). Verbatim here as `original_source.md`. Read 2026-10-16 (FMZ-C).
- Status: PORTED (batch C21). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; bracket fixed at entry (arming approximation stated). |
| 2 | ADAPT | Tick distances -> ATR multiples. |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | The bracket is ported via stops() and quoted in original_sizing.txt. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | DG428811. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`tp_atr` [0.15, 1.0] x `sl_atr` [0.15, 1.0]: **4 trials**; EMAs 50 / 100, stochastic 4 / 3, MACD 12 / 26 / 10 fixed.

## Ambiguities resolved

- The bracket is armed from the entry (the source arms it on touch bars). A same-bar long and short: the long is kept.
- REVERSAL INTENDED. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "multi_indicator_confluence"`.

## Marks

`none`
