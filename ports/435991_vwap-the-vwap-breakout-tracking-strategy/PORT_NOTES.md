# #435991 VWAP突破追踪策略The-VWAP-breakout-tracking-strategy -> `fmz_435991_vwap_push_high_low_breakout_5m_reversal`

- FMZ source id: 435991 (lineage).
- Source: https://www.fmz.com/strategy/435991 (PineScript v5, author ChaoZhang, FMZ last
  modified 2023-12-20 16:25:18). Verbatim here as `original_source.md`. Read 2026-10-23 (FMZ-C).
- Status: PORTED (batch V18). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | VWAP push breakouts with VWAP exits |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | Strategy(): 100 % of equity, capital 100000, pyramiding 0, not ported. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`push_len` [3, 2]: **2 trials**.

## Ambiguities resolved

- Session VWAP from the broker-day start. Volume = broker tick volume. REVERSAL INTENDED. FREQ = "5min".

## FAMILY (proposed, user to confirm)

`FAMILY = "vwap_breakout"`.

## Marks

`none`
