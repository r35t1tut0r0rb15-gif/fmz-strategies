# #432228 双均线Stoch指标二元期权交易策略Dual-Moving-Average-Stochastic-Indicator-Binary-Options-Trading-Strategy -> `fmz_432228_ema_band_stoch_fade`

- FMZ source id: 432228 (lineage).
- Source: https://www.fmz.com/strategy/432228 (PineScript v2, author ChaoZhang, FMZ last
  modified 2023-11-15 16:56:47). Verbatim here as `original_source.md`. Read 2026-10-17 (FMZ-C).
- Status: PORTED (batch C50). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | EMA bands and stochastic levels |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`band_len` [4, 8] x `ema_len` [21, 50]: **4 trials**; stochastic 14 / 1 / 3 fixed.

## Ambiguities resolved

- A fade as written. REVERSAL INTENDED. FREQ = "3min".

## FAMILY (proposed, user to confirm)

`FAMILY = "stochastic_oscillator"`.

## Marks

`none`
