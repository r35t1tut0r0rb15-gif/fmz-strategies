# #435776 Momentum Breakthrough Moving Average Trading Strategy -> `fmz_435776_ema458_cross_volume_spike_3m_pct_bracket_reversal`

- FMZ source id: 435776 (lineage).
- Source: https://www.fmz.com/strategy/435776 (PineScript v5, author ChaoZhang, FMZ last
  modified 2023-12-18 18:01:59). Verbatim here as `original_source.md`. Read 2026-10-23 (FMZ-C).
- Status: PORTED (batch V17). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; percent bracket from the fill |
| 2 | PASS | Long-EMA crossings on volume spikes |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`ema_len` [458, 200] x `vol_mult` [1.5, 2.0]: **4 trials**; volume EMA 21, SL 1 %, TP 2 %.

## Ambiguities resolved

- Bracket from the fill. Volume = broker tick volume. REVERSAL INTENDED. FREQ = "3min".

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_cross"`.

## Marks

`none`
