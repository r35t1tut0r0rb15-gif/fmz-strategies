# #361969 QQE-MOD-SSL-Hybrid-Waddah-Attar-Explosion -> `fmz_361969_qqe_ssl_wae_confluence`

- Source: https://www.fmz.com/strategy/361969 (PineScript v5, author ChaoZhang, FMZ last
  modified 2022-05-09 12:01:14). Verbatim here as `original_source.md`. Read 2026-10-07 (worker A).
- Status: PORTED (batch A6). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close entries; a resting swing stop (sl_stop). |
| 2 | PASS | Oscillators, ATR-like ranges and BB widths; the swing stop is a bar level. |
| 3 | PASS | Binance futures pair in the header only. |
| 4 | DONE | Risk-based quantity (2 % of equity over the stop distance) -> `original_sizing.txt`. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`baseline_len` [40, 60, 90] x `swing_len` [5, 10, 20] x `sensitivity` [120, 180] = **18 trials**. QQE, WAE and exit-line settings fixed at the source defaults.

## Ambiguities resolved

- Only the default MA types are ported (HMA baseline, HMA exit line); the SSL2 'continuation' line (JMA) is not used by the orders.
- The stop is re-based on the fill price (vbt sl_stop); simulate() mirrors it only to know when the position is flat.
- Stops on 4-hour bars: mark `coarse_bar_stop` (rule 4).
- The date-range inputs (2022-2023) are a backtest window and are dropped.
- `FREQ = "4h"` from the backtest header.

## FAMILY (proposed, user to confirm)

`FAMILY = "multi_indicator_confluence"`.

## Marks (2026-10-07)

`coarse_bar_stop`
