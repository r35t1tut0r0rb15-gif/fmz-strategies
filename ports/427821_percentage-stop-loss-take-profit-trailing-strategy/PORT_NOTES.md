# #427821 Percentage Stop Loss Take Profit Trailing Strategy -> `fmz_427821_sma200_cross_pct_bracket_long`

- FMZ source id: 427821 (lineage).
- Source: https://www.fmz.com/strategy/427821 (PineScript v3, author ChaoZhang, FMZ last
  modified 2023-09-25 18:09:14). Verbatim here as `original_source.md`. Read 2026-10-16 (FMZ-C).
- Status: PORTED (batch C12). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close entries; bracket fixed at entry. |
| 2 | PASS | Percentages only. |
| 3 | PASS | Spot pair in the header only. |
| 4 | DONE | No sizing code; bracket quoted. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`sma_per` [200, 100] x `sl_pct` [2, 1] x `tp_pct` [1, 2]: **8 trials**; defaults 200 / 2 / 1 (the source's).

## Ambiguities resolved

- Percent-of-entry levels: `sl_stop` 0.02, `tp_stop` 0.01; nothing trails despite the title.
- Stop module: `portfolio_kwargs` `{}`. Long only. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_cross"`.

## Marks

`none`
