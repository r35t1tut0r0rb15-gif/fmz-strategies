# #365095 Shannon Entropy V2 -> `fmz_365095_shannon_entropy_close_log_volume_pctrank_extreme_reversal`

- FMZ source id: 365095 (lineage).
- Source: https://www.fmz.com/strategy/365095 (PineScript v4, author ChaoZhang, FMZ last
  modified 2022-05-24 10:13:21). Verbatim here as `original_source.md`. Read 2026-10-23 (FMZ-C).
- Status: PORTED (batch V2). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Entropy percent-rank extremes |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`len` [9, 20] x `avg` [44, 100]: **4 trials**; percent rank limit 2.

## Ambiguities resolved

- Volume = broker tick volume (log). REVERSAL INTENDED. FREQ = "2h".

## FAMILY (proposed, user to confirm)

`FAMILY = "momentum_oscillator"`.

## Marks

`none`
