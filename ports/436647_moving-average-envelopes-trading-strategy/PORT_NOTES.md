# #436647 Moving Average Envelopes Trading Strategy -> `fmz_436647_ma_envelope_state`

- FMZ source id: 436647 (lineage).
- Source: https://www.fmz.com/strategy/436647 (PineScript v2, author ChaoZhang, FMZ last
  modified 2023-12-26 15:55:43). Verbatim here as `original_source.md`. Read 2026-10-18 (FMZ-C).
- Status: PORTED (batch C94). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Envelope breakout state |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`length` [14, 28] x `percent_shift` [1.0, 2.0]: **4 trials**; the reverse switch (off) fixed.

## Ambiguities resolved

- State entries sent on every bar of the state. REVERSAL INTENDED. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "volatility_channel_breakout"`.

## Marks

`none`
