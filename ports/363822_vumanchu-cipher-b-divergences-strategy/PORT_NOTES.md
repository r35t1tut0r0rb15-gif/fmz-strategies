# #363822 VuManChu Cipher B Divergences Strategy -> `fmz_363822_wavetrend_line_order_divergence_exit_reversal`

- FMZ source id: 363822 (lineage).
- Source: https://www.fmz.com/strategy/363822 (PineScript v4, author ChaoZhang, FMZ last
  modified 2022-05-17 15:24:47). Verbatim here as `original_source.md`. Read 2026-10-23 (FMZ-C).
- Status: PORTED (batch V2). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | WaveTrend line order with cross and divergence exits |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code (the commented strategy() line: cash 10000). |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | DG363822. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`wt_channel_len` [9, 14] x `wt_average_len` [12, 21]: **4 trials**; MA 3, OB / OS 53, divergence limits 45 / -65, 15 / -40.

## Ambiguities resolved

- Volume not used (the "MFI" is a body ratio). REVERSAL INTENDED. FREQ = "2h".

## FAMILY (proposed, user to confirm)

`FAMILY = "wavetrend_oscillator"`.

## Marks

`none`
