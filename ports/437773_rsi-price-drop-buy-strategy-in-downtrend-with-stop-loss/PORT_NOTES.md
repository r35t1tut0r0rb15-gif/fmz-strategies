# #437773 RSI收敛破位趋势震荡停损策略Price-Drop-Buy-Strategy-in-Downtrend-with-Stop-Loss -> `fmz_437773_bb_dip_buy_profit_flip`

- FMZ source id: 437773 (lineage).
- Source: https://www.fmz.com/strategy/437773 (PineScript v3, author ChaoZhang, FMZ last
  modified 2024-01-05 14:18:05). Verbatim here as `original_source.md`. Read 2026-10-21 (FMZ-C).
- Status: PORTED (batch C105). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | ADAPT | Price-unit open-profit test -> fraction of the entry |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | The capital stored. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`rsi_length` [60, 30] x `profit_frac` [0.0012, 0.01]: **4 trials**; BB 20 x 2 and oversold 40 fixed.

## Ambiguities resolved

- Always-true overbought constant; open profit of 50 units -> fraction of the entry. REVERSAL INTENDED. FREQ = "30min".

## FAMILY (proposed, user to confirm)

`FAMILY = "mean_reversion"`.

## Marks

`none`
