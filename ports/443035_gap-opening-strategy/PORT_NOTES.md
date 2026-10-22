# #443035 Gap Opening Strategy -> `fmz_443035_range_expansion_sma20_wick_exit_long`

- FMZ source id: 443035 (lineage).
- Source: https://www.fmz.com/strategy/443035 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-02-28 17:12:52). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C165). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Range expansion with an SMA filter; lower-wick exit |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`ma_length` [20, 50] x `exit_below` [0.98, 0.95]: **4 trials**; the HL length fixed.

## Ambiguities resolved

- Same-bar entry stands; wick exit on held longs. Long only. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "volatility_channel_breakout"`.

## Marks

`none`
