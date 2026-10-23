# #376259 EtHEriOOOm 30MIN -> `fmz_376259_adx_range_filter_vwma_volume_mfi_stoch_scalp_confluence_reversal`

- FMZ source id: 376259 (lineage).
- Source: https://www.fmz.com/strategy/376259 (PineScript, no @version line, author a624587332, FMZ last
  modified 2022-08-02 23:44:45). Verbatim here as `original_source.md`. Read 2026-10-23 (FMZ-C).
- Status: PORTED (batch V3). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; short-only bracket as fractions of the fill |
| 2 | PASS | Multi-indicator trend confluence with a stochastic scalp |
| 3 | PASS | No exchange header. |
| 4 | DONE | 100 % of equity, capital 10000 and commission 0.04 % stored, not ported. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`rvol_trigger` [1.1, 1.5] x `th` [16.0, 25.0]: **4 trials**; the other settings as written.

## Ambiguities resolved

- The shared exit id leaves longs without a bracket, as written (weird case). Bar size from the title (30MIN).
- Window dropped. Volume = broker tick volume. REVERSAL INTENDED. FREQ = "30min".

## FAMILY (proposed, user to confirm)

`FAMILY = "multi_indicator_confluence"`.

## Marks

`trailing_stop_pending`
