# #362103 EHMA-Range-Strategy -> `fmz_362103_ehma_band_reverse`

- Source: https://www.fmz.com/strategy/362103 (PineScript, author ChaoZhang, FMZ last
  modified 2022-05-10 00:01:08). Verbatim here as `original_source.md`. Read 2026-10-07 (worker A).
- Status: PORTED (batch A7). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders. |
| 2 | ADAPT | +/-2 % band -> +/- `band_atr` x ATR(14). |
| 3 | PASS | Binance futures pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`period` [90, 180, 270] x `band_atr` [0.25, 0.5, 1] = **9 trials**.

## Ambiguities resolved

- Position type 'Both' (default); the Long/Short-only options are not split versions (rule 6).
- Warm-up of 2 x period bars for the zero-seeded EMAs.
- `FREQ = "1D"` broker days from the backtest header.

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_envelope_breakout"`.

## Marks (2026-10-07)

`none`
