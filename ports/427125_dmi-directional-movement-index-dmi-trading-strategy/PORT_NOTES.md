# #427125 Directional Movement Index DMI Trading Strategy -> `fmz_427125_dmi_strong_up_long`

- FMZ source id: 427125 (lineage).
- Source: https://www.fmz.com/strategy/427125 (PineScript v5, author ChaoZhang, FMZ last
  modified 2023-09-18 14:11:21). Verbatim here as `original_source.md`. Read 2026-10-15 (FMZ-C).
- Status: PORTED (batch C1). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders (calc_on_every_tick false). |
| 2 | PASS | DI / ADX levels. |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | 100 % of equity, commission, slippage stored in `original_sizing.txt`. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`di_length` [7, 14] x `adx_smoothing` [14, 7] x `adx_level` [25, 20]: **8 trials**; defaults 7 / 14 / 25 (the source's).

## Ambiguities resolved

- trade_type is the constant 'Long': long only; the "Both" / "Short" branches never run.
- The test-date window is the author's backtest window: dropped.
- fixnan is causal (last earlier value); ta.tr is na on the first bar.
- FREQ = "30min" from the backtest header.

## FAMILY (proposed, user to confirm)

`FAMILY = "directional_movement"`.

## Marks

`none`
