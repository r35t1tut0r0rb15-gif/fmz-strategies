# #429150 Dynamic Strategy Analytics Tool -> `fmz_429150_rsi7_momentum_cross`

- FMZ source id: 429150 (lineage).
- Source: https://www.fmz.com/strategy/429150 (PineScript v5, author ChaoZhang, FMZ last
  modified 2023-10-13 15:54:35). Verbatim here as `original_source.md`. Read 2026-10-16 (FMZ-C).
- Status: PORTED (batch C23). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders. |
| 2 | PASS | RSI levels only. |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | The commented-out strategy() stored. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`rsi_length` [7, 14] x `upper` [70, 60]: **4 trials**; the lower level is 100 - upper (30 at the default).

## Ambiguities resolved

- The statistics table is display only. REVERSAL INTENDED. FREQ = "3h".

## FAMILY (proposed, user to confirm)

`FAMILY = "rsi_oscillator"`.

## Marks

`none`
