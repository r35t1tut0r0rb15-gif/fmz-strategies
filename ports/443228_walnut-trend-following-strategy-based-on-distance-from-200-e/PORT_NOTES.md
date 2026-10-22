# #443228 Walnut Trend Following Strategy Based on Distance from 200 EMA -> `fmz_443228_ema200_stretch_one_bar_hold`

- FMZ source id: 443228 (lineage).
- Source: https://www.fmz.com/strategy/443228 (PineScript v4, author ChaoZhang, FMZ last
  modified 2024-03-01 10:50:03). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C167). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | EMA stretch entries; one-bar holds as written |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`ema_period` [200, 100] x `threshold` [0.75, 1.5]: **4 trials**.

## Ambiguities resolved

- time_close() read as true: one-bar holds. Entries only from flat. FREQ = "3h".

## FAMILY (proposed, user to confirm)

`FAMILY = "mean_reversion"`.

## Marks

`none`
