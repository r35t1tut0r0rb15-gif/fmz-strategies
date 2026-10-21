# #437390 随机Fisher变换临时停止反转STOCH指标量化策略Random-Fisher-Transform-Temporary-Stop-Reverse-STOCH-Indicator-Quantitative-Strategy -> `fmz_437390_inverse_fisher_stoch_trail`

- FMZ source id: 437390 (lineage).
- Source: https://www.fmz.com/strategy/437390 (PineScript v3, author ChaoZhang, FMZ last
  modified 2024-01-02 11:14:12). Verbatim here as `original_source.md`. Read 2026-10-21 (FMZ-C).
- Status: PORTED (batch C100). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; the trail is a house trail (approximation stated) |
| 2 | ADAPT | Tick trail -> ATR multiple and a fraction |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | The percent-of-equity size, commission and the tick trail inputs stored. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`stoch_len` [19, 14] x `trail_k` [0.002, 1.0]: **4 trials**; smooth 4, levels 0.64 / -0.62, activation 0.0006 fixed.

## Ambiguities resolved

- Tick trail as a house volatility trail (stated approximation). REVERSAL INTENDED. Marks coarse_bar_stop, trailing_stop. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "stochastic_oscillator"`.

## Marks

`coarse_bar_stop, trailing_stop`
