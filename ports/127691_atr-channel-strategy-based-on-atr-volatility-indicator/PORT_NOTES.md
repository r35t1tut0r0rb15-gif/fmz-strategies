# #127691 基于ATR波动率指标构建的通道策略 -> `fmz_127691_atr_channel_stop_and_reverse`

- Source: https://www.fmz.com/strategy/127691 (MyLanguage, author Zero, FMZ last modified
  2018-12-21 16:13:58). Verbatim here as `original_source.md`. Read 2026-10-07 (worker A).
- Status: PORTED (batch A1). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Close-price model, completed bars. |
| 2 | ADAPT | 2 % stop -> `sl_atr` x the source's ATR(N); the 8 % (M x 2 %) profit-exit activation -> M x that distance. |
| 3 | PASS | BitMEX XBTUSD in the header only. |
| 4 | DONE | One lot per signal; no sizing code. `original_sizing.txt` records that. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | Group `ND127691` (0.65-0.80): partner #128126 (Jaccard 0.73). Reading shows #128126 is the same logic with the same defaults (parameters written as arguments instead of constants) -> #128126 set aside as `DUPLICATE_ON_READING` of this port (an exact duplicate in behaviour). |
| 7 | IGNORED | |

## Declared grid (criterion 5)

`n` [100, 200, 300] x `m` [2, 3, 4] x `sl_atr` [1, 2, 3] = **27 trials**.

## Ambiguities resolved

- One signal per bar in source order: the BPK/SPK breakouts are checked before the exits, so a
  bar that makes a new N-bar high while short reverses (BPK) rather than only covering.
- `BKHIGH` counts the bars after the entry signal bar, current bar included.
- `FREQ = "1h"` from the backtest header.

## FAMILY (proposed, user to confirm)

`FAMILY = "donchian_breakout"`: always-in N-bar high/low breakout reversal.

## Marks (2026-10-07)

`none`
