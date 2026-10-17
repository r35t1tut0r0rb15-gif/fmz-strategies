# #432896 基于SMA的多空策略SMA-Based-Dual-Thrust-Strategy -> `fmz_432896_sma_high_low_channel`

- FMZ source id: 432896 (lineage).
- Source: https://www.fmz.com/strategy/432896 (PineScript v4, author ChaoZhang, FMZ last
  modified 2023-11-22 15:42:29). Verbatim here as `original_source.md`. Read 2026-10-17 (FMZ-C).
- Status: PORTED (batch C55). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Channel crosses and percentage offsets |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | Qty 1 stored in original_sizing.txt. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`length` [20, 50] x `offset` [1.0, 0.5]: **4 trials** (offset in % for the exit lines).

## Ambiguities resolved

- Both exits on the SMA of the highs, as written. REVERSAL INTENDED. FREQ = "10min".

## FAMILY (proposed, user to confirm)

`FAMILY = "donchian_breakout"`.

## Marks

`none`
