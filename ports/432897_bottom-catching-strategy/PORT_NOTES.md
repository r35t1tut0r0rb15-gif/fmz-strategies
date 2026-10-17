# #432897 Bottom Catching Strategy -> `fmz_432897_rsi_drop_death_cross_long`

- FMZ source id: 432897 (lineage).
- Source: https://www.fmz.com/strategy/432897 (PineScript v5, author ChaoZhang, FMZ last
  modified 2023-11-22 15:46:19). Verbatim here as `original_source.md`. Read 2026-10-17 (FMZ-C).
- Status: PORTED (batch C55). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | RSI levels and SMA crosses |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`rsi_len` [14, 9] x `drop` [3.0, 1.0]: **4 trials**; the SMA crosses and the 40 / 65 levels fixed.

## Ambiguities resolved

- SMAs as written. Long only. FREQ = "1min".

## FAMILY (proposed, user to confirm)

`FAMILY = "rsi_oscillator"`.

## Marks

`none`
