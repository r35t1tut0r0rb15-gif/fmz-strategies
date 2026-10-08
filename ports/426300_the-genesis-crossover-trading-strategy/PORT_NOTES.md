# #426300 The Genesis Crossover Trading Strategy -> `fmz_426300_genesis_ema_cross_short_bracket`

- Source: https://www.fmz.com/strategy/426300 (PineScript v5, author ChaoZhang, FMZ last
  modified 2023-09-10 21:38:32). Verbatim here as `original_source.md`. Read 2026-10-07 (worker A).
- Status: PORTED (batch A20). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders. |
| 2 | ADAPT | Tick distances -> ATR(14) multiples at the signal bar. |
| 3 | PASS | Exchange pair in the header only (if any). |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`sl_atr` [0.25, 0.5, 1.0]: **3 trials**; EMA 20 / 50 and the 5:1 target ratio fixed (the source's constants). The default 0.25 is the smallest step (the source's 2 ticks are near zero ATR).

## Ambiguities resolved

- As written, the long exit names entry "Long" (the entry is "long") and the short exit re-issues the same id "Exit": only shorts are bracketed. Kept as written (decision owed: likely a typo).
- Criterion 2 (ADAPT): ticks -> sl_atr x ATR(14) at the signal bar, target 5x; NaN for long entries.
- Daily bars are broker days; stops on daily bars: coarse_bar_stop.

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_trend"`.

## Marks (2026-10-07)

`coarse_bar_stop`
