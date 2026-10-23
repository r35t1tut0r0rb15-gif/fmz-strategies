# #440538 量化W形态高手之路Quant-W-Pattern-Master-Strategy -> `fmz_440538_sma14_28_cross_dead_w_pattern_1h_reversal`

- FMZ source id: 440538 (lineage).
- Source: https://www.fmz.com/strategy/440538 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-01-31 14:49:56). Verbatim here as `original_source.md`. Read 2026-10-23 (FMZ-C).
- Status: PORTED (batch V25). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | SMA 14 / 28 crossings |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`fast` [14, 10] x `slow` [28, 50]: **4 trials**.

## Ambiguities resolved

- The W pattern entry is dead as written. Volume not used. REVERSAL INTENDED. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_cross"`.

## Marks

`none`
