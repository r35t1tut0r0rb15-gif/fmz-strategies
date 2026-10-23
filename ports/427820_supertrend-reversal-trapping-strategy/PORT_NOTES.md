# #427820 SuperTrend Reversal Trapping Strategy -> `fmz_427820_supertrend2_10_small_trap_candle_volume_reversal`

- FMZ source id: 427820 (lineage).
- Source: https://www.fmz.com/strategy/427820 (PineScript v5, author ChaoZhang, FMZ last
  modified 2023-09-25 17:58:05). Verbatim here as `original_source.md`. Read 2026-10-23 (FMZ-C).
- Status: PORTED (batch V7). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Counter-candle entries in a SuperTrend with volume confirmation |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | Margin_long / margin_short 1 stored, not ported. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`factor` [2.0, 3.0] x `candle_divider` [0.003, 0.0015]: **4 trials**; ATR 10.

## Ambiguities resolved

- Volume = broker tick volume. REVERSAL INTENDED. FREQ = "5min".

## FAMILY (proposed, user to confirm)

`FAMILY = "supertrend"`.

## Marks

`none`
