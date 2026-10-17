# #432788 动量突破TTM策略Momentum-Breakthrough-TTM-Strategy -> `fmz_432788_ttm_squeeze_burst_time_exit`

- FMZ source id: 432788 (lineage).
- Source: https://www.fmz.com/strategy/432788 (PineScript v4, author ChaoZhang, FMZ last
  modified 2023-11-21 15:07:38). Verbatim here as `original_source.md`. Read 2026-10-17 (FMZ-C).
- Status: PORTED (batch C54). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; explicit time exits |
| 2 | ADAPT | Price-unit momentum thresholds -> ATR multiples |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | Pyramiding 1999 and the initial capital stored in original_sizing.txt. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`osc_atr` [0.0, 0.1] x `hold` [5, 3]: **4 trials**; TTM 20, BB 50 x 0.2, RSI 30 and the levels fixed.

## Ambiguities resolved

- Momentum thresholds as ATR multiples (0 = as written in effect). Time exits after 5 bars. REVERSAL INTENDED. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "volatility_squeeze"`.

## Marks

`none`
