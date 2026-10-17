# #430878 Bull Market Buy Dips Strategy -> `fmz_430878_bull_dip_rsi_long`

- FMZ source id: 430878 (lineage).
- Source: https://www.fmz.com/strategy/430878 (PineScript v4, author ChaoZhang, FMZ last
  modified 2023-11-02 16:21:21). Verbatim here as `original_source.md`. Read 2026-10-17 (FMZ-C).
- Status: PORTED (batch C41). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | RSI level and SMA comparisons |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | 30 % of equity and the commission stored in original_sizing.txt. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`rsi_len` [14, 7] x `rsi_buy` [35, 25]: **4 trials**; SMA 9 / 50 / 200 fixed.

## Ambiguities resolved

- Entry and close on one bar: flat if already long, long if flat. Long only. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "rsi_oscillator"`.

## Marks

`none`
