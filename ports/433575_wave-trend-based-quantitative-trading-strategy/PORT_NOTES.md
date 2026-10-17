# #433575 Wave Trend Based Quantitative Trading Strategy -> `fmz_433575_wavetrend_friday_close`

- FMZ source id: 433575 (lineage).
- Source: https://www.fmz.com/strategy/433575 (PineScript v4, author ChaoZhang, FMZ last
  modified 2023-11-28 16:17:31). Verbatim here as `original_source.md`. Read 2026-10-17 (FMZ-C).
- Status: PORTED (batch C62). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; a clock-time exit signal |
| 2 | PASS | Oscillator levels |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`tz` ["UTC", "America/New_York"] x `n1` [10, 20]: **4 trials**; average 21 and the levels fixed.

## Ambiguities resolved

- Friday close-out in UTC or New York, both declared. REVERSAL INTENDED. FREQ = "1min".

## FAMILY (proposed, user to confirm)

`FAMILY = "momentum_oscillator_turn"`.

## Marks

`none`
