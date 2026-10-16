# #430558 MACD-收盘中位海龟混合策略MACD-Closing-Turtle-Hybrid-Strategy -> `fmz_430558_macd_hist_hybrid`

- FMZ source id: 430558 (lineage).
- Source: https://www.fmz.com/strategy/430558 (PineScript v4, author ChaoZhang, FMZ last
  modified 2023-10-30 12:16:20). Verbatim here as `original_source.md`. Read 2026-10-16 (FMZ-C).
- Status: PORTED (batch C36). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders. |
| 2 | PASS | MACD histogram states. |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | The commented-out cash order size stored in original_sizing.txt. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`reenter_delay` [2, 3] x `sculp_delay` [4, 6]: **4 trials**; MACD 12 / 26 / 9 (SMA signal) fixed.

## Ambiguities resolved

- Last entry on a bar sets the side; closes act on the start position unless reversed. REVERSAL INTENDED. FREQ = "2h".

## FAMILY (proposed, user to confirm)

`FAMILY = "macd_momentum"`.

## Marks

`none`
