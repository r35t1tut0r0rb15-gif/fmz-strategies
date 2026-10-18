# #435266 Momentum Breakout and Trend Following Combination Strategy -> `fmz_435266_supertrend_stoch_swing_bracket`

- FMZ source id: 435266 (lineage).
- Source: https://www.fmz.com/strategy/435266 (PineScript v4, author ChaoZhang, FMZ last
  modified 2023-12-13 16:41:25). Verbatim here as `original_source.md`. Read 2026-10-18 (FMZ-C).
- Status: PORTED (batch C76). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; bracket fixed at entry |
| 2 | PASS | Average trend, supertrend, stochastic and swing stop |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | The risk-based lot size stored. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`pl` [1.5, 2.0] x `factor` [3.0, 2.0]: **4 trials**; ATR 10, stochastic 8 / 3 / 3, EMA 25 / 50 / 100 / 200 fixed.

## Ambiguities resolved

- Entry from flat by the house bracket; invalid stop skipped. Opposite entries cannot occur. FREQ = "1min".

## FAMILY (proposed, user to confirm)

`FAMILY = "supertrend"`.

## Marks

`none`
