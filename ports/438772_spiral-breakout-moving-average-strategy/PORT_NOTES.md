# #438772 Spiral Breakout Moving Average Strategy -> `fmz_438772_ssl_roc_chaikin_mf_cross_2pct_stop_45m_reversal`

- FMZ source id: 438772 (lineage).
- Source: https://www.fmz.com/strategy/438772 (PineScript v4, author ChaoZhang, FMZ last
  modified 2024-01-15 11:45:23). Verbatim here as `original_source.md`. Read 2026-10-23 (FMZ-C).
- Status: PORTED (batch V21). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; fixed 2 % stop from the fill |
| 2 | PASS | SSL channel direction with momentum, or Chaikin money-flow crossings |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | Percent_of_equity 100 and commission 0.075 %, not ported. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`sl_pct` [0.02, 0.04] x `cmf_len` [20, 10]: **4 trials**; SSL 12 / 13, ROC 13, thresholds 0.04 / 0.02.

## Ambiguities resolved

- Later call wins on a two-sided bar; stop armed at the fill. Volume = broker tick volume (CMF). REVERSAL INTENDED. FREQ = "45min".

## FAMILY (proposed, user to confirm)

`FAMILY = "ssl_hybrid"`.

## Marks

`none`
