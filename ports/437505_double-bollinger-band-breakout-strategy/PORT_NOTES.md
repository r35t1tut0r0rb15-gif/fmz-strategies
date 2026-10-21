# #437505 Double Bollinger Band Breakout Strategy -> `fmz_437505_double_bollinger_breakout`

- FMZ source id: 437505 (lineage).
- Source: https://www.fmz.com/strategy/437505 (PineScript v4, author ChaoZhang, FMZ last
  modified 2024-01-03 12:06:31). Verbatim here as `original_source.md`. Read 2026-10-21 (FMZ-C).
- Status: PORTED (batch C101). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; stop fixed at entry |
| 2 | PASS | Bollinger bands; stop beyond the signal bar's extreme |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | The percent-of-equity size, commission and the stop inputs stored. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | ND434998. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`length_slow` [45, 50] x `length_fast` [31, 20]: **4 trials**; RSI 14, 1 sigma, 1 % stop increment fixed.

## Ambiguities resolved

- Strategy Stop from the signal bar's extreme (one bar early, stated); no target; other stop types off. REVERSAL INTENDED. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "bollinger_breakout"`.

## Marks

`coarse_bar_stop`
