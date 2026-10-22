# #451072 Advanced-MACD-Strategy-with-Limited-Martingale-基于有限马丁格尔的高级MACD策略 -> `fmz_451072_macd15_30_cross_one_pct_close_tests_reversal`

- FMZ source id: 451072 (lineage).
- Source: https://www.fmz.com/strategy/451072 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-05-11 17:24:43). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C184). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; exits are close tests against the fill |
| 2 | PASS | MACD crossings with 1 % close tests |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | The martingale quantity and capital stored. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | DG451072. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`band` [0.01, 0.02] x `fast` [15, 12]: **4 trials**; the slow and signal lengths fixed.

## Ambiguities resolved

- Martingale is sizing. REVERSAL INTENDED. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "macd_cross"`.

## Marks

`none`
