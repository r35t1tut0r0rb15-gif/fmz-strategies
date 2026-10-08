# #391341 SSL Channel + Stoch RSI -> `fmz_391341_ssl_stochrsi_bracket`

- Source: https://www.fmz.com/strategy/391341 (PineScript v5, author luqi0212, FMZ last
  modified 2022-11-24 11:56:41). Verbatim here as `original_source.md`. Read 2026-10-07 (worker A).
- Status: PORTED (batch A18). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders. |
| 2 | ADAPT | Profit / loss 10000 ticks -> `bracket_atr` x ATR(14). |
| 3 | PASS | Exchange pair in the header only (if any). |
| 4 | DONE | Order-size lines -> `original_sizing.txt`. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | Group `ND365858` (Jaccard 0.65-0.80) with #365858 (PORT_CANDIDATE); best Jaccard 0.703 with #365858. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`ssl_slow` [100, 200] x `ssl_fast` [10, 20] x `bracket_atr` [5.0, 10.0, 20.0] (stop = target, as the defaults) = **12 trials**.

## Ambiguities resolved

- Profit/loss 10000 ticks -> `bracket_atr` x ATR(14) at the signal bar (criterion 2), tp/sl fractions shifted one bar.
- `A or B and C and D` reads A or (B and C and D) (Pine precedence). A same-bar long and short cancel each other (no order).
- `FREQ = "5min"` from the backtest header.

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_envelope_breakout"`.

## Marks (2026-10-07)

`none`
