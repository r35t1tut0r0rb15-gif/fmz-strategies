# #437029 RSI指标改进交易策略RSI-Indicator-Improvement-Trading-Strategy -> `fmz_437029_rsi_histo_level_state`

- FMZ source id: 437029 (lineage).
- Source: https://www.fmz.com/strategy/437029 (PineScript v2, author ChaoZhang, FMZ last
  modified 2023-12-29 16:23:48). Verbatim here as `original_source.md`. Read 2026-10-21 (FMZ-C).
- Status: PORTED (batch C99). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | RSI levels |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`period` [13, 21] x `buy_level` [-10.0, 0.0]: **4 trials**; sell level 10 and modifier 1.5 fixed; reverse off.

## Ambiguities resolved

- Overlapping levels as written. REVERSAL INTENDED. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "rsi_oscillator"`.

## Marks

`none`
