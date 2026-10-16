# #429148 Dual Smooth Moving Average Trading Strategy -> `fmz_429148_nnfx_ssl_tdfi`

- FMZ source id: 429148 (lineage).
- Source: https://www.fmz.com/strategy/429148 (PineScript v3, author ChaoZhang, FMZ last
  modified 2023-10-13 15:45:58). Verbatim here as `original_source.md`. Read 2026-10-16 (FMZ-C).
- Status: PORTED (batch C23). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; the moving bracket is not emitted (rule 2). |
| 2 | PASS | Channel flips and a normalised index. |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | The commented-out strategy() stored; the bracket quoted in original_sizing.txt. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`ssl1` [8, 5] x `ssl2` [16, 30]: **4 trials**; TDFI 6 / +-0.05 and the ATR settings fixed.

## Ambiguities resolved

- Pending (not emitted): on every bar while long, a stop at that bar's close - 1.5 x ATR(14, SMA of
  the true range) and a limit at close + 1 x ATR (shorts mirrored), re-issued each bar.
- REVERSAL INTENDED. FREQ = "2D" (blocks of 2 broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "ssl_channel"`.

## Marks

`trailing_stop_pending`
