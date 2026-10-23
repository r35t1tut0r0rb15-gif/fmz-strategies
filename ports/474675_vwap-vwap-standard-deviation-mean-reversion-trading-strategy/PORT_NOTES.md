# #474675 VWAP标准差回归均值交易策略-VWAP-Standard-Deviation-Mean-Reversion-Trading-Strategy -> `fmz_474675_cumulative_vwap_2sd_fade_vwap_exit_1m_reversal`

- FMZ source id: 474675 (lineage).
- Source: https://www.fmz.com/strategy/474675 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-12-11 15:06:33). Verbatim here as `original_source.md`. Read 2026-10-23 (FMZ-C).
- Status: PORTED (batch V34). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Fades of deviation bands around a cumulative VWAP |
| 3 | PASS | Exchange pair in the header only (ETHUSD named in the title). |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`std_mult` [2.0, 3.0] x `length` [20, 60]: **4 trials**.

## Ambiguities resolved

- Cumulative VWAP from the data start. Volume = broker tick volume. REVERSAL INTENDED. FREQ = "1min".

## FAMILY (proposed, user to confirm)

`FAMILY = "vwap"`.

## Marks

`none`
