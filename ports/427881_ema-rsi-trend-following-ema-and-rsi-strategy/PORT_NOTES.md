# #427881 Trend Following EMA and RSI Strategy -> `fmz_427881_alorse_ema_rsi_long`

- FMZ source id: 427881 (lineage).
- Source: https://www.fmz.com/strategy/427881 (PineScript v5, author ChaoZhang, FMZ last
  modified 2023-09-26 15:39:48). Verbatim here as `original_source.md`. Read 2026-10-16 (FMZ-C).
- Status: PORTED (batch C13). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; bar count and entry price known at the close. |
| 2 | PASS | MA lengths, RSI level, bar count. |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | Commented strategy() sizing stored. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`x_bars` [24, 12] x `len_c` [100, 200]: **4 trials**; defaults 24 / 100 (the source's); RSI 14 (exit 70), EMAs 10 / 20 fixed.

## Ambiguities resolved

- Entry price = the fill bar's open; the bar count starts on the fill bar.
- Short entries off by default: Long only. strategy() commented out. FREQ = "2h".

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_cross"`.

## Marks

`none`
