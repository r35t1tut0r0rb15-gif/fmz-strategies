# #442927 Momentum Reversal Strategy Based on Multiple Timeframes -> `fmz_442927_wide_body_impulse_bar_pct_bracket`

- FMZ source id: 442927 (lineage).
- Source: https://www.fmz.com/strategy/442927 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-02-27 14:27:49). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C163). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; bracket fixed at entry |
| 2 | PASS | Wide-body impulse bars |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`range_mult` [2.0, 1.5] x `tp_pct` [0.003, 0.01]: **4 trials**; the body share and the stop fixed.

## Ambiguities resolved

- Bracket as fixed fractions of the fill. REVERSAL INTENDED. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "candle_pattern"`.

## Marks

`none`
