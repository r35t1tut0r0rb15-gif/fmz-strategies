# #361785 Ks-Reversal-Indicator-I -> `fmz_361785_ks_band_macd_reversal`

- Source: https://www.fmz.com/strategy/361785 (PineScript v5, author ChaoZhang (Sofien Kaabar indicator), FMZ last
  modified 2022-05-08 11:14:32). Verbatim here as `original_source.md`. Read 2026-10-07 (worker A).
- Status: PORTED (batch A5). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Uses bars [1] and [2] plus the current mid; bar-close orders. |
| 2 | PASS | Bands and MACD cross only. |
| 3 | PASS | Binance futures pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`length` [50, 100, 200] x `multiplier` [1.5, 2, 2.5] = **9 trials**. MACD 12/26/9 fixed.

## Ambiguities resolved

- Mixed bar references (previous candle vs current mid) kept as written.
- `FREQ = "30min"` from the backtest header.

## FAMILY (proposed, user to confirm)

`FAMILY = "bollinger_reversion"`: band-extreme candle plus a turn confirmation, traded for reversal

## Marks (2026-10-07)

`none`
