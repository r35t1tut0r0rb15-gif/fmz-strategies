# #435987 Momentum Tracking Trading Strategy -> `fmz_435987_candle_colour_bracket`

- FMZ source id: 435987 (lineage).
- Source: https://www.fmz.com/strategy/435987 (PineScript v5, author ChaoZhang, FMZ last
  modified 2023-12-20 16:06:26). Verbatim here as `original_source.md`. Read 2026-10-18 (FMZ-C).
- Status: PORTED (batch C84). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; bracket fixed at entry |
| 2 | REVIEW | Clock inputs unused; tick bracket -> ATR multiple |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | The tick-bracket inputs quoted in original_sizing.txt. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`direction` ["Forward", "Inverse"] x `k_atr` [0.1, 1.0]: **4 trials**.

## Ambiguities resolved

- Anchor hour unused (candle test on every bar); tick bracket -> ATR multiple. REVERSAL INTENDED. FREQ = "30min".

## FAMILY (proposed, user to confirm)

`FAMILY = "candle_pattern"`.

## Marks

`none`
