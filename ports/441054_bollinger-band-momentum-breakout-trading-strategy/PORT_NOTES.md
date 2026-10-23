# #441054 Bollinger Band Momentum Breakout Trading Strategy -> `fmz_441054_buying_volume_bollinger_breakout_profit_exits_1h_reversal`

- FMZ source id: 441054 (lineage).
- Source: https://www.fmz.com/strategy/441054 (PineScript v4, author ChaoZhang, FMZ last
  modified 2024-02-05 10:53:46). Verbatim here as `original_source.md`. Read 2026-10-23 (FMZ-C).
- Status: PORTED (batch V26). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; close-based exits in the signals |
| 2 | PASS | Buying-volume Bollinger breakouts with profit-protecting exits |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`length` [20, 50] x `daily_len` [50, 20]: **4 trials**; deviations 1 / 1.5 / 2, RSI 14.

## Ambiguities resolved

- openprofit read with the default 1-unit order (5 % stop). Volume = broker tick volume. REVERSAL INTENDED. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "bollinger_breakout"`.

## Marks

`none`
