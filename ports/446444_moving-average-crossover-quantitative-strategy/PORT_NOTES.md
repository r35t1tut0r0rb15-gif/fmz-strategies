# #446444 Moving Average Crossover Quantitative Strategy -> `fmz_446444_sma9_20_latched_cross_green_confirm_long`

- FMZ source id: 446444 (lineage).
- Source: https://www.fmz.com/strategy/446444 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-03-28 16:55:42). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C174). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Latched SMA cross with a confirming bar, SMA 9 exit |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`fast` [9, 5] x `slow` [20, 50]: **4 trials**.

## Ambiguities resolved

- Long only. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_cross"`.

## Marks

`none`
