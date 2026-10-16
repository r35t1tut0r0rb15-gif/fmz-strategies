# #430855 Adaptive Moving Average Channel Breakout Strategy -> `fmz_430855_durenard_ama_channel`

- FMZ source id: 430855 (lineage).
- Source: https://www.fmz.com/strategy/430855 (PineScript v4, author ChaoZhang, FMZ last
  modified 2023-11-02 15:05:56). Verbatim here as `original_source.md`. Read 2026-10-16 (FMZ-C).
- Status: PORTED (batch C40). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders. |
| 2 | PASS | Returns, an adaptive average and ratios. |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`beta` [2.1, 1.5] x `snr_factor` [2.1, 1.2]: **4 trials**; look-back 5 fixed.

## Ambiguities resolved

- Integer division in nwma as Pine v4 computes it. REVERSAL INTENDED. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "volatility_channel_breakout"`.

## Marks

`none`
