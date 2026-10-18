# #435869 Bollinger Band Breakout Trading Strategy -> `fmz_435869_bollinger_fallback_long_pause`

- FMZ source id: 435869 (lineage).
- Source: https://www.fmz.com/strategy/435869 (PineScript v5, author ChaoZhang, FMZ last
  modified 2023-12-19 14:08:45). Verbatim here as `original_source.md`. Read 2026-10-18 (FMZ-C).
- Status: PORTED (batch C82). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; stop fixed at entry |
| 2 | REVIEW | The pause is relative to the last position change |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | The cash size, leverage and risk inputs stored. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`lookback` [25, 40] x `dev_mult` [2.0, 1.5]: **4 trials**; stop 1 %, factor 2 and the pause of 6 hours fixed.

## Ambiguities resolved

- Pause from the last position change; stop followed as the house bracket; close-based take profit. Long only. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "bollinger_breakout"`.

## Marks

`none`
