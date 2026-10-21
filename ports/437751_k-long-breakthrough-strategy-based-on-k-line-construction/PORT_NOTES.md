# #437751 基于K线构建的多头突破策略Long-Breakthrough-Strategy-Based-on-K-Line-Construction -> `fmz_437751_outside_reversal_bar_pct_bracket_long`

- FMZ source id: 437751 (lineage).
- Source: https://www.fmz.com/strategy/437751 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-01-05 12:37:46). Verbatim here as `original_source.md`. Read 2026-10-21 (FMZ-C).
- Status: PORTED (batch C105). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; bracket fixed at entry |
| 2 | PASS | Candle pattern and percent bracket |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | The percent-of-equity size, capital and commission stored. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`tp` [0.04, 0.02] x `sl` [0.04, 0.02]: **4 trials**.

## Ambiguities resolved

- Tick bracket read as fixed percents of the entry. Long only. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "candle_pattern"`.

## Marks

`none`
