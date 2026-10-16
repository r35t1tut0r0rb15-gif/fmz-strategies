# #427921 Trading Strategy Based on Hull Moving Average and WT Cross -> `fmz_427921_kalman_hull_wavetrend`

- FMZ source id: 427921 (lineage).
- Source: https://www.fmz.com/strategy/427921 (PineScript v5, author ChaoZhang, FMZ last
  modified 2023-09-26 20:00:32). Verbatim here as `original_source.md`. Read 2026-10-16 (FMZ-C).
- Status: PORTED (batch C14). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; bracket fixed at entry. |
| 2 | PASS | MA lengths and percentages. |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | 100 % of equity stored; exits quoted. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`lookback` [24, 48] x `sl_pct` [5, 2.5] x `tp_pct` [10, 5]: **8 trials**; defaults 24 / 5 / 10 (the source's); WT 10 / 21 and gain 10000 fixed.

## Ambiguities resolved

- Default switches: WT cross on, second method off, Kalman on. The else-if branches never add an order; closes coincide with the opposite entries.
- hma3 uses close and p = 12 as written; the HMA crosses are strict on both sides as written.
- `sl_stop` 0.05, `tp_stop` 0.10. Stop module: `portfolio_kwargs` `{}`; REVERSAL INTENDED. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "hull_ma"`.

## Marks

`none`
