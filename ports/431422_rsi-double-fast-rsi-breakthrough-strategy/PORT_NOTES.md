# #431422 快速RSI指标二次突破策略Double-Fast-RSI-Breakthrough-Strategy -> `fmz_431422_noro_double_fast_rsi`

- FMZ source id: 431422 (lineage).
- Source: https://www.fmz.com/strategy/431422 (PineScript v2, author ChaoZhang, FMZ last
  modified 2023-11-07 16:56:39). Verbatim here as `original_source.md`. Read 2026-10-17 (FMZ-C).
- Status: PORTED (batch C45). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | RSI levels and bar colour / body filters |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | The capital % lot formula stored in original_sizing.txt. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`limit` [25, 15] x `rsi2_len` [14, 21]: **4 trials**; RSI 7 and the body filters fixed; both limits equal.

## Ambiguities resolved

- close_all after an entry leaves the bar flat. REVERSAL INTENDED. FREQ = "15min".

## FAMILY (proposed, user to confirm)

`FAMILY = "rsi_oscillator"`.

## Marks

`none`
