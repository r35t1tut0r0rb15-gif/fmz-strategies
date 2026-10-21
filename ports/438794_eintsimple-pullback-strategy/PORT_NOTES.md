# #438794 EintSimple Pullback Strategy -> `fmz_438794_simple_pullback_ema75_9_long`

- FMZ source id: 438794 (lineage).
- Source: https://www.fmz.com/strategy/438794 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-01-15 14:04:54). Verbatim here as `original_source.md`. Read 2026-10-21 (FMZ-C).
- Status: PORTED (batch C112). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; close-tested exits |
| 2 | PASS | EMA pullback and close tests |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | The capital and percent-of-equity size stored. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | DG438794, ND438794. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`ma1` [75, 200] x `stop` [0.10, 0.05]: **4 trials**; EMA 9 and lower-close exit fixed.

## Ambiguities resolved

- Stop tested from the bar after the fill; close-tested exits. Long only. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "mean_reversion"`.

## Marks

`none`
