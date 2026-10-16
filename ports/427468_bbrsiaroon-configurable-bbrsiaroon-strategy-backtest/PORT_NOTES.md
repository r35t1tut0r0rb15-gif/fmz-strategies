# #427468 Configurable BBRSIAroon Strategy Backtest -> `fmz_427468_bb_rsi_aroonish`

- FMZ source id: 427468 (lineage).
- Source: https://www.fmz.com/strategy/427468 (PineScript v4, author ChaoZhang, FMZ last
  modified 2023-09-21 15:05:38). Verbatim here as `original_source.md`. Read 2026-10-16 (FMZ-C).
- Status: PORTED (batch C8). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; bar-count exits. |
| 2 | PASS | Oscillator levels, bands, bar counts. |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`bb_mult` [2.5, 2] x `rsi_length` [4, 8] x `n_bars` [3, 6]: **8 trials**; defaults 2.5 / 4 / 3 (the source's); Aroonish 4 / 50, RSI 20 / 80, BB 20 fixed.

## Ambiguities resolved

- The "Aroonish" lines use `-highestbars`, not the classic Aroon: ported literally.
- The exit fires 3 bars after the signal (`ConditionLong[nBars]`), an explicit exit signal. REVERSAL INTENDED. FREQ = "5min".

## FAMILY (proposed, user to confirm)

`FAMILY = "multi_indicator_confluence"`.

## Marks

`none`
