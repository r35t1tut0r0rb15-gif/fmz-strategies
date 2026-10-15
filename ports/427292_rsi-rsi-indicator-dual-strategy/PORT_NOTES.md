# #427292 RSI Indicator Dual Strategy -> `fmz_427292_4all_v3_rsi_extremes`

- FMZ source id: 427292 (lineage).
- Source: https://www.fmz.com/strategy/427292 (PineScript v3, author ChaoZhang, FMZ last
  modified 2023-09-19 19:43:19). Verbatim here as `original_source.md`. Read 2026-10-15 (FMZ-C).
- Status: PORTED (batch C4). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close entries; exits are bar-close tests of high / low (signals). |
| 2 | ADAPT | tp 15 / sl 23 ten-thousandths (pips) -> ATR(14) multiples. |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | Leverage / liquidation and the (off) trailing input stored. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`rsi_band` [5, 10] x `tp_atr` [1, 2] x `sl_atr` [1.5, 3]: **8 trials**; defaults 5 / 1.0 / 1.5; RSI 4 fixed. On a 1-hour FX pair 15 / 23 pips are about 1 / 1.5-2 ATR (judgement, stated before any backtest).

## Ambiguities resolved

- The reference price is the OPEN of the signal bar (`last_open_long_signal`), not the fill; tp / sl are measured from it, in ATR of the signal bar.
- The exits are `strategy.close` on completed-bar tests (rule 3): next-open fills.
- Trailing distance 99999 / 10000 = off; liquidation exits depend on leverage (sizing): neither ported.
- REVERSAL INTENDED. FREQ = "1h" from the backtest header.

## FAMILY (proposed, user to confirm)

`FAMILY = "rsi_oscillator"`.

## Marks

`none`
