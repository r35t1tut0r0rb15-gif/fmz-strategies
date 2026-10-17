# #434699 基于价格通道和MACD的多时间框架交易策略Price-Channel-and-MACD-Based-Multi-Timeframe-Trading-Strategy -> `fmz_434699_sonic_r_macd_colour`

- FMZ source id: 434699 (lineage).
- Source: https://www.fmz.com/strategy/434699 (PineScript v2, author ChaoZhang, FMZ last
  modified 2023-12-08 15:15:37). Verbatim here as `original_source.md`. Read 2026-10-17 (FMZ-C).
- Status: PORTED (batch C70). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Channel-relative bar shapes and MACD states |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code; the unused exit inputs quoted in original_sizing.txt. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`hilo_len` [34, 89] x `fast` [12, 6]: **4 trials**; MACD slow 26 / signal 9 fixed.

## Ambiguities resolved

- Exit orders off as written. REVERSAL INTENDED. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "macd_momentum"`.

## Marks

`none`
