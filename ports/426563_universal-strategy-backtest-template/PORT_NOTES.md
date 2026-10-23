# #426563 Universal Strategy Backtest Template -> `fmz_426563_template_rsi10_over80_both_entries_rsi100_close_reversal`

- FMZ source id: 426563 (lineage).
- Source: https://www.fmz.com/strategy/426563 (PineScript v5, author ChaoZhang, FMZ last
  modified 2023-09-13 12:28:06). Verbatim here as `original_source.md`. Read 2026-10-23 (FMZ-C).
- Status: PORTED (batch V5). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; close-based stop and RSI exits; target from the fill |
| 2 | PASS | RSI threshold demo rule (as written) |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | Contracts = equity / close x leverage, 100 % of equity, capital 20000, commission 0.075 stored, not ported. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`entry_level` [80.0, 70.0] x `sl` [0.15, 0.05]: **4 trials**; RSI 10 / 100, exits 40 / 60, TP 100 %.

## Ambiguities resolved

- shortCondition = longConditionEntry, as written (weird case). REVERSAL INTENDED. FREQ = "1min".

## FAMILY (proposed, user to confirm)

`FAMILY = "rsi_threshold"`.

## Marks

`none`
