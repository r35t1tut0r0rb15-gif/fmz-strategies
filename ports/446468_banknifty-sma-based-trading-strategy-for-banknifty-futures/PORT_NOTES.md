# #446468 基于均线的BankNifty期货交易策略-SMA-based-Trading-Strategy-for-BankNifty-Futures -> `fmz_446468_sma200_body_rejection_point_exits_5m`

- FMZ source id: 446468 (lineage).
- Source: https://www.fmz.com/strategy/446468 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-03-28 18:15:32). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C175). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; exits are close tests against the fill |
| 2 | PASS | SMA rejections with SMA, point and clock exits |
| 3 | PASS | BankNifty in the title only; no exchange header; the point values read as fractions of the price. |
| 4 | DONE | The qty 15 and the margins stored. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`length` [200, 100] x `target_frac` [0.00357, 0.01]: **4 trials**; the stop fraction and the clock exit fixed.

## Ambiguities resolved

- Bar size 5 minutes from the chart input (no header); points as fractions of 42000; hour 15 UTC. FREQ = "5min".

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_pullback"`.

## Marks

`none`
