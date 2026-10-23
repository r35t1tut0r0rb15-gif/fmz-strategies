# #434296 EMA-ADX-VOL-加密货币杀手EMA-ADX-VOL-CRYPTO-KILLER -> `fmz_434296_adx_range_filter_ema_stack_volume_spike_pct_bracket_reversal`

- FMZ source id: 434296 (lineage).
- Source: https://www.fmz.com/strategy/434296 (PineScript v4, author ChaoZhang, FMZ last
  modified 2023-12-05 11:03:37). Verbatim here as `original_source.md`. Read 2026-10-23 (FMZ-C).
- Status: PORTED (batch V15). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; percent bracket from the fill |
| 2 | PASS | ADX, range filter, EMA stack and volume-spike confluence |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | Strategy(): 100 % of equity, capital 10000, pyramiding 1, commission 0.03 %, not ported. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`volume_f` [3.2, 2.0] x `adx_th` [20.0, 25.0]: **4 trials**; ADX 21, range filter 15 x 2.6, EMAs 8-55, TP 0.9 %, SL 4.2 %.

## Ambiguities resolved

- Exit distances as #376261 (nLongs <= 1). Title 15M, header 1d used. Volume = broker tick volume. REVERSAL INTENDED. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "adx_volume_confluence"`.

## Marks

`coarse_bar_stop, trailing_stop_pending`
