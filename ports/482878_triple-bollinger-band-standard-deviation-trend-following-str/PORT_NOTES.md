# #482878 三重布林带标准差趋势跟踪策略-Triple-Bollinger-Band-Standard-Deviation-Trend-Following-Strategy -> `fmz_482878_three_closes_outside_band_flat_1r`

- FMZ source id: 482878 (lineage).
- Source: https://www.fmz.com/strategy/482878 (PineScript v6, author ianzeng123, FMZ last
  modified 2025-02-20 16:16:14). Verbatim here as `original_source.md`. Read 2026-10-17 (FMZ-C laptop lane).
- Status: PORTED (batch L25). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; bracket from the signal bar. |
| 2 | PASS | Bollinger bands and the setup's own extremes. |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | 10 % of equity quoted; the bracket via `stops()` and quoted. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`mult` [2.0, 1.5] x `rr` [1.0, 2.0]: **4 trials**; defaults 2 / 1 (the source's); BB 20 fixed.

## Ambiguities resolved

- The stop at the first setup bar's low (high) and the 1 R target become fractions of the signal close by side,
  re-based on the fill; a signal whose stop is not beyond the close emits no entry (as #490798).
- Entries only from flat: `simulate()` mirrors the house bracket from the fill bar (as #430254 `_run`). Opposite
  entries cannot occur. Stop module: `portfolio_kwargs` {} (D4). FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "breakout"`.

## Marks

`none`
