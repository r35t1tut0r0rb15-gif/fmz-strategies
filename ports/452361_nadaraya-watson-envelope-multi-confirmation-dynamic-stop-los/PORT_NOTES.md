# #452361 Nadaraya Watson Envelope Multi Confirmation Dynamic Stop Loss Strategy -> `fmz_452361_nadaraya_watson_breakout_dmi_rsi_trail_close_reversal`

- FMZ source id: 452361 (lineage).
- Source: https://www.fmz.com/strategy/452361 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-05-24 17:58:47). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C188). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; the close-based trailing exit in a loop |
| 2 | PASS | Kernel-envelope breakouts with DMI / RSI confirmation |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`bandwidth` [7.2, 4.0] x `mult` [2.1, 3.0] x `adx_min` [25, 20]: **8 trials**; the 15 % give-back and the RSI levels fixed.

## Ambiguities resolved

- Close-based 15 % give-back exit in a loop. REVERSAL INTENDED. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "volatility_channel_breakout"`.

## Marks

`none`
