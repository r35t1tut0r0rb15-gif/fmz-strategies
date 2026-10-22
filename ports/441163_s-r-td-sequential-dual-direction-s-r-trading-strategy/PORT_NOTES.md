# #441163 量化交易双向S-R策略TD-Sequential-Dual-Direction-S-R-Trading-Strategy -> `fmz_441163_td_sequential_9_sma10_revert_sma200_bracket`

- FMZ source id: 441163 (lineage).
- Source: https://www.fmz.com/strategy/441163 (PineScript v4, author ChaoZhang, FMZ last
  modified 2024-02-06 12:13:22). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C148). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; bracket fixed at entry |
| 2 | ADAPT | Tick bracket from the close -> fixed fractions |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`price_flip` [9, 13] x `exit_len` [10, 20]: **4 trials**; trend SMA 200 and the 1 % bracket fixed.

## Ambiguities resolved

- Default block only; setup on the ninth count; tick bracket as fixed fractions. REVERSAL INTENDED. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "reversal_pattern"`.

## Marks

`coarse_bar_stop`
