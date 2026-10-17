# #430903 威廉姆累积-分配指标Williams-AD策略Williams-Accumulation-Distribution-Williams-AD-Strategy -> `fmz_430903_williams_ad_sign`

- FMZ source id: 430903 (lineage).
- Source: https://www.fmz.com/strategy/430903 (PineScript v2, author ChaoZhang, FMZ last
  modified 2023-11-02 17:25:51). Verbatim here as `original_source.md`. Read 2026-10-17 (FMZ-C).
- Status: PORTED (batch C42). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | The sign of a cumulative price sum |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | ND430903. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

No parameter reaches the orders ("Trade reverse" stays false): **1 trial**, the source as written.

## Ambiguities resolved

- Unchanged close resets the sum, as written. REVERSAL INTENDED. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "momentum_oscillator_turn"`.

## Marks

`none`
