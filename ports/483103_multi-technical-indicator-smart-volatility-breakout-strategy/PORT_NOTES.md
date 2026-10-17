# #483103 多重技术指标智能波动突破策略-Multi-Technical-Indicator-Smart-Volatility-Breakout-Strategy -> `fmz_483103_bb_stoch_atr_spike_long_bracket`

- FMZ source id: 483103 (lineage).
- Source: https://www.fmz.com/strategy/483103 (PineScript v5, author ianzeng123, FMZ last
  modified 2025-02-21 13:42:44). Verbatim here as `original_source.md`. Read 2026-10-17 (FMZ-C laptop lane).
- Status: PORTED (batch L20). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; bracket from the signal bar (re-placement marked). |
| 2 | PASS | Bollinger bands, a stochastic and ATR multiples. |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | 10 % of equity quoted; the bracket via `stops()` and quoted. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`atr_mult` [1.5, 1.0] x `bb_mult` [2.0, 2.5]: **4 trials**; defaults 1.5 / 2 (the source's); BB 20, stochastic
14 / 3 / 3 and ATR 14 fixed. `atr_mult` sets both the ATR threshold and the bracket, as written.

## Trailing stop (mark `trailing_stop_pending`)

A buy signal while held re-places the stop and target from the new close. The port keeps the entry's bracket.

## Ambiguities resolved

- `ta.stdev` is the population standard deviation. Long only: opposite entries cannot occur; the sell close is an exit
  signal. Stop module: `portfolio_kwargs` {} (D4). FREQ = "1min".

## FAMILY (proposed, user to confirm)

`FAMILY = "mean_reversion"`.

## Marks

`trailing_stop_pending`
