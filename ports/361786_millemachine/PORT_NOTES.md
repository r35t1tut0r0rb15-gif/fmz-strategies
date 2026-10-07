# #361786 MilleMachine -> `fmz_361786_hma_turn_mcginley_filter`

- Source: https://www.fmz.com/strategy/361786 (PineScript v4, author ChaoZhang (Milleman script), FMZ last
  modified 2022-05-08 16:22:45). Verbatim here as `original_source.md`. Read 2026-10-07 (worker A).
- Status: PORTED (batch A5). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close entries/exits; a resting stop order (sl_stop). |
| 2 | PASS | ATR-based stop; MA turns. |
| 3 | PASS | No venue code. |
| 4 | DONE | Risk-based quantity (1 % of equity over the stop distance) -> `original_sizing.txt`. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`ei_len` [30, 46, 60] x `bl_len` [30, 50, 100] x `atr_mult` [1.5, 2, 3] = **27 trials**.

## Ambiguities resolved

- **Trailing stop pending (rule 2)**: while in a long, the stop is raised to `EMA(low, 5) x (1 - SL)` whenever that is higher (short: lowered to `EMA(high, 2) x (1 + SL)`), SL = 2 ATR(14)/(close + 2 ATR) of the current bar. Not emitted; only the initial stop is (sl_stop).
- The initial stop level is the signal close x (1 -/+ SL); vbt applies the same fraction to the fill price (next open).
- After a stop-out simulate() still counts the position until the next HMA turn (it cannot see fills); since entries need a flat position and an HMA turn, the only lost case is a short entry on the same turn that would have closed the stopped long.
- Only the default MA types (McGinley baseline, HMA entry, EMA trail) are ported; Mode LongShort.
- No backtest header: `FREQ = "bar_size_pending"` (rule 1).

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_trend"`.

## Marks (2026-10-07)

`bar_size_pending, trailing_stop_pending`
