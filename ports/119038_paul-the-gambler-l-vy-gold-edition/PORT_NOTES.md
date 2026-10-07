# #119038 Paul-The-Gambler-Lévy-Gold-Edition -> `fmz_119038_rsi_slope_reverse_on_stop`

- Source: https://www.fmz.com/strategy/119038 (Python, author FawkesPan, FMZ last modified
  2018-09-28 16:53:43). Repository copy `Paul-The-Gambler-Lévy-Gold-Edition.md`; verbatim here as
  `original_source.md`. Read 2026-09-29.
- Status: PORTED (batch 1), signals only. Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS (with note) | RSI slope on completed bars. Target/stop are evaluated on bar closes, not intrabar, because the reverse-after-stop rule must know the stop fired; declared change of fill timing. |
| 2 | ADAPT | 1.5 % stop / 3 % target -> `sl_atr` / `tp_atr` x ATR(14) on the signal bar. |
| 3 | PASS (screen: REVIEW) | Uses a weekly crypto futures contract and leverage, but only as the venue. The signals need no funding, order book or swap mechanics. |
| 4 | DONE | Martingale (AMP x size up to RISK_LIMIT), START_SIZE, leverage, contract, +/-1 % marketable prices -> `original_sizing.txt`. |
| 5 | DECLARED | See grid. |
| 6 | REPRESENTATIVE | No duplicate group; no possible-duplicate pairs. |
| 7 | IGNORED | The description warns it will lose all money in live trading; that is not used either way. |

## Declared grid (criterion 5)

`sl_atr` [1, 2, 3] x `tp_atr` [2, 4, 6] = **9 trials**. RSI period (hard-coded 14 in the original)
and ATR length 14 are fixed. The original's target is twice its stop; the grid keeps 2:1 on its
diagonal and brackets it.

## Ambiguities resolved

- "Randomly open a position" (line 186) is in fact the RSI-slope rule on lines 187-193; that is
  the entry signal.
- After a take-profit the position is flat and the next bar re-enters by RSI slope; after a stop
  the opposite position opens (reversal). Both are reproduced; the doubling is sizing.
- `FREQ = "bar_size_pending"` (was `"1h"` until 2026-10-07): the source declares no period. Rule 2026-10-07: never choose a bar size; mark `bar_size_pending`. Logic unchanged.

## FAMILY (proposed, user to confirm)

`FAMILY = "stop_and_reverse_bracket"`. RSI slope only picks the opening side; the logic that drives the trades is the fixed target/stop bracket and the reversal after a stop. Alternative if you prefer grouping by indicator: rsi_oscillator (with #11604).
Added 2026-10-03 in the contract fix pass.

## Marks (2026-10-07)

`bar_size_pending`
