# #442937 Dynamic Trailing Stop Strategy -> `fmz_442937_last_minute_flip_trail_line_reversal`

- FMZ source id: 442937 (lineage).
- Source: https://www.fmz.com/strategy/442937 (PineScript v3, author ChaoZhang, FMZ last
  modified 2024-02-27 15:02:34). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C163). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; the 1-minute values end with the day |
| 2 | ADAPT | Price-unit offsets -> fractions of the price |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`long_frac` [0.00544, 0.02] x `short_frac` [0.0058, 0.02]: **4 trials**.

## Ambiguities resolved

- Last-minute values; price-unit offsets as fractions. REVERSAL INTENDED. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "volatility_channel_breakout"`.

## Marks

`none`
