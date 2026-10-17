# #430868 BB双重多空头交易策略BB-Dual-Long-and-Short-Trading-Strategy -> `fmz_430868_bb_fade_pct_exits`

- FMZ source id: 430868 (lineage).
- Source: https://www.fmz.com/strategy/430868 (PineScript v5, author ChaoZhang, FMZ last
  modified 2023-11-02 15:40:00). Verbatim here as `original_source.md`. Read 2026-10-17 (FMZ-C).
- Status: PORTED (batch C41). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; close-checked exits. |
| 2 | PASS | Bollinger bands and percentage exits. |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`length` [20, 50] x `take_p` [5.0, 2.0]: **4 trials**; 2 sd and the 1 % stop fixed.

## Ambiguities resolved

- Close-checked exits from the signal close. FREQ = "2min".

## FAMILY (proposed, user to confirm)

`FAMILY = "bollinger_reversion"`.

## Marks

`none`
