# #451487 Triple Relative Strength Index Quantitative Trading Strategy -> `fmz_451487_triple_falling_rsi5_dip_above_sma200_long`

- FMZ source id: 451487 (lineage).
- Source: https://www.fmz.com/strategy/451487 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-05-15 10:23:08). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C185). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Falling-RSI dips above the SMA 200 |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`rsi_len` [5, 3] x `sma_len` [200, 100]: **4 trials**; the levels 35 / 60 / 50 fixed.

## Ambiguities resolved

- Long only. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "rsi_oscillator"`.

## Marks

`none`
