# #440467 Trend Following Strategy Based on Multiple Indicators -> `fmz_440467_dragon_bot_bb_stochrsi_atr_step`

- FMZ source id: 440467 (lineage).
- Source: https://www.fmz.com/strategy/440467 (PineScript v3, author ChaoZhang, FMZ last
  modified 2024-01-30 17:51:04). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C135). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; close-tested exits |
| 2 | PASS | Bollinger levels, stochastic RSI and an ATR step trail |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | DG440467. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`sellprofit` [1.0, 3.0] x `atr_multi` [1.0, 2.0]: **4 trials**; BB and stochastic RSI settings fixed.

## Ambiguities resolved

- Close-tested exits; short profit test as written. Entries only from flat. FREQ = "2h".

## FAMILY (proposed, user to confirm)

`FAMILY = "bollinger_reversion"`.

## Marks

`none`
