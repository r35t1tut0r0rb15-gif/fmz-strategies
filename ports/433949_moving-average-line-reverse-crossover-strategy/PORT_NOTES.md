# #433949 Moving Average Line Reverse Crossover Strategy -> `fmz_433949_sma_cross_down_8bar_short`

- FMZ source id: 433949 (lineage).
- Source: https://www.fmz.com/strategy/433949 (PineScript v5, author ChaoZhang, FMZ last
  modified 2023-12-01 16:52:13). Verbatim here as `original_source.md`. Read 2026-10-17 (FMZ-C).
- Status: PORTED (batch C64). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; bar-count exit signal |
| 2 | PASS | An SMA cross |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`ma_len` [45, 90] x `hold` [8, 16]: **4 trials**.

## Ambiguities resolved

- Dead second entry clause dropped. Short only. FREQ = "5min".

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_cross"`.

## Marks

`none`
