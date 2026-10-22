# #442835 Intelligent Accumulator Buy Strategy -> `fmz_442835_rsi7_own_band_dip_long`

- FMZ source id: 442835 (lineage).
- Source: https://www.fmz.com/strategy/442835 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-02-26 13:59:57). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C161). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | RSI against its own deviation band |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`rsi_len` [7, 14] x `band_len` [14, 30]: **4 trials**.

## Ambiguities resolved

- One long at a time (default pyramiding). Long only. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "rsi_oscillator"`.

## Marks

`none`
