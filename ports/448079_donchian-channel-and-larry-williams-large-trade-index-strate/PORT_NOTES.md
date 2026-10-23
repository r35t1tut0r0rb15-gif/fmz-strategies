# #448079 Donchian Channel and Larry Williams Large Trade Index Strategy -> `fmz_448079_donchian96_breakout_lwti_volume_basis_target_1m`

- FMZ source id: 448079 (lineage).
- Source: https://www.fmz.com/strategy/448079 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-04-12 17:27:25). Verbatim here as `original_source.md`. Read 2026-10-23 (FMZ-C).
- Status: PORTED (batch V29). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; basis-distance target from the fill |
| 2 | PASS | Donchian breakouts with LWTI and volume filters, one trade per basis cross |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`don_length` [96, 48] x `rr` [2.0, 1.0]: **4 trials**; LWTI 25, volume SMA 30.

## Ambiguities resolved

- Shared exit id: the stop is replaced by the target. Volume = broker tick volume. REVERSAL INTENDED. FREQ = "1min".

## FAMILY (proposed, user to confirm)

`FAMILY = "volatility_channel_breakout"`.

## Marks

`none`
