# #429333 Wick Reversal Pattern Strategy -> `fmz_429333_wick_reversal`

- FMZ source id: 429333 (lineage).
- Source: https://www.fmz.com/strategy/429333 (PineScript v4, author ChaoZhang, FMZ last
  modified 2023-10-16 08:58:12). Verbatim here as `original_source.md`. Read 2026-10-16 (FMZ-C).
- Status: PORTED (batch C23). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders. |
| 2 | ADAPT | The price-unit doji threshold -> an ATR multiple. |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`wick_mult` [3.25, 2.5] x `body_mult` [1.1, 1.5]: **4 trials**; body percentage 0.35, 50-bar RMA and the doji ATR fraction fixed.

## Ambiguities resolved

- Doji threshold as an ATR multiple. REVERSAL INTENDED. FREQ = "3min".

## FAMILY (proposed, user to confirm)

`FAMILY = "candle_pattern"`.

## Marks

`none`
