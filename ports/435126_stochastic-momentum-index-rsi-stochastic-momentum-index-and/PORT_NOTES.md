# #435126 基于Stochastic-Momentum-Index和RSI的量化策略Stochastic-Momentum-Index-and-RSI-Based-Quant-Trading-Strategy -> `fmz_435126_noro_smi_rsi_fade`

- FMZ source id: 435126 (lineage).
- Source: https://www.fmz.com/strategy/435126 (PineScript v2, author ChaoZhang, FMZ last
  modified 2023-12-12 15:20:29). Verbatim here as `original_source.md`. Read 2026-10-17 (FMZ-C).
- Status: PORTED (batch C74). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Oscillator extremes with bar filters |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | The equity lot and the martingale option stored. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`limitsmi` [50, 30] x `limitrsi` [10, 20]: **4 trials**; SMI 2 / 2, RSI 2 and the filters fixed.

## Ambiguities resolved

- Same-bar entry beats the close. REVERSAL INTENDED. FREQ = "5min".

## FAMILY (proposed, user to confirm)

`FAMILY = "stochastic_oscillator"`.

## Marks

`none`
