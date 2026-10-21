# #436763 三重超趋势Ichimoku云量化交易策略Triple-Supertrend-Ichimoku-Cloud-Quantitative-Trading-Strategy -> `fmz_436763_triple_supertrend_open_margin`

- FMZ source id: 436763 (lineage).
- Source: https://www.fmz.com/strategy/436763 (PineScript v5, author ChaoZhang, FMZ last
  modified 2023-12-27 15:22:40). Verbatim here as `original_source.md`. Read 2026-10-21 (FMZ-C).
- Status: PORTED (batch C95). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Supertrend lines with an ATR margin |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | The unused percent-of-portfolio input stored. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`atr_len` [14, 21] x `factor1` [1.0, 1.5]: **4 trials**; the other two lines (11 / 2, 12 / 3) and the first ATR period 10 fixed.

## Ambiguities resolved

- State entries sent on every bar of the state; plotted-only lines left out. REVERSAL INTENDED. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "supertrend"`.

## Marks

`none`
