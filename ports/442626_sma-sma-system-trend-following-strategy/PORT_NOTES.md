# #442626 基于SMA均线系统的趋势跟踪策略SMA-System-Trend-Following-Strategy -> `fmz_442626_close_sma3_cross_reversal`

- FMZ source id: 442626 (lineage).
- Source: https://www.fmz.com/strategy/442626 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-02-23 12:29:51). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C159). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | ADAPT | The tick-scaled stop never acts on the BTC reading |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`slow` [3, 10] x `fast` [1, 2]: **4 trials**.

## Ambiguities resolved

- Stop below zero, not ported. REVERSAL INTENDED. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_cross"`.

## Marks

`none`
