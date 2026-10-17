# #431278 Super Ichi Strategy -> `fmz_431278_superichi_pullback`

- FMZ source id: 431278 (lineage).
- Source: https://www.fmz.com/strategy/431278 (PineScript v5, author ChaoZhang, FMZ last
  modified 2023-11-06 16:32:11). Verbatim here as `original_source.md`. Read 2026-10-17 (FMZ-C).
- Status: PORTED (batch C44). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; bracket fixed at entry |
| 2 | PASS | ATR-banded averages, swing extremes and a reward ratio |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | The 2 % account-risk quantity stored in original_sizing.txt. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`swing_len` [15, 30] x `rr` [2.0, 1.0]: **4 trials**; SuperIchi settings, ATR 14 x 1 and the 5-bar pull-back fixed.

## Ambiguities resolved

- Bracket fixed at the signal. Mark coarse_bar_stop. REVERSAL INTENDED. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "ichimoku"`.

## Marks

`coarse_bar_stop`
