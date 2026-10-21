# #436754 利用双向RSI突破策略Dual-RSI-Breakthrough-Strategy -> `fmz_436754_rsi_threshold_alternating_bracket`

- FMZ source id: 436754 (lineage).
- Source: https://www.fmz.com/strategy/436754 (PineScript v4, author ChaoZhang, FMZ last
  modified 2023-12-27 14:33:15). Verbatim here as `original_source.md`. Read 2026-10-21 (FMZ-C).
- Status: PORTED (batch C95). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; bracket fixed at entry |
| 2 | ADAPT | Tick amounts -> ATR multiples |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | The risk lot formula and the pip inputs stored. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`period` [14, 21] x `k_atr` [0.6, 1.5]: **4 trials**; thresholds 75 / 25, the 10:1 target and ATR 14 fixed; inverse off.

## Ambiguities resolved

- Tick amounts -> ATR multiples; signals alternate through the myPosition flag; session strings unused. REVERSAL INTENDED. FREQ = "3min".

## FAMILY (proposed, user to confirm)

`FAMILY = "rsi_oscillator"`.

## Marks

`none`
