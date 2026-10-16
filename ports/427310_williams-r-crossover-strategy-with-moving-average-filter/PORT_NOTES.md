# #427310 Williams R Crossover Strategy with Moving Average Filter -> `fmz_427310_williams_r_cross_ma200`

- FMZ source id: 427310 (lineage).
- Source: https://www.fmz.com/strategy/427310 (PineScript v5, author ChaoZhang, FMZ last
  modified 2023-09-19 21:57:46). Verbatim here as `original_source.md`. Read 2026-10-15 (FMZ-C).
- Status: PORTED (batch C5). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; close-based exits. |
| 2 | ADAPT | "pips / mintick" distances -> ATR(14) multiples. |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`cross` [10, 20] x `tp_atr` [1.5, 3] x `sl_atr` [1, 2]: **8 trials**; defaults 10 / 1.5 / 1; %R 14, SMA 200 fixed. On the source's 1-hour BTC bars with a 0.1 tick the as-written distances are 300 / 200 USD, about 1.5 / 1 ATR (judgement, stated before any backtest).

## Ambiguities resolved

- `pips / syminfo.mintick` (evidently meant as a multiply) is instrument-specific: ATR multiples instead.
- Exits compare the close with the entry fill price (next open after the signal): exit signals (rule 3).
- REVERSAL INTENDED. FREQ = "1h" from the backtest header.

## FAMILY (proposed, user to confirm)

`FAMILY = "williams_r_oscillator"`.

## Marks

`none`
