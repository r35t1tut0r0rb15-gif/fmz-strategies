# #376263 Bitcoin Scalper 30MIN -> `fmz_376263_rmi_mfi_pivot_cloud_ha_scalp_sets_short_bracket_reversal`

- FMZ source id: 376263 (lineage).
- Source: https://www.fmz.com/strategy/376263 (PineScript v4, author a624587332, FMZ last
  modified 2022-08-02 23:58:55). Verbatim here as `original_source.md`. Read 2026-10-23 (FMZ-C).
- Status: PORTED (batch V3). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; short-only bracket as fractions of the fill |
| 2 | PASS | RMI / money-flow / Heikin-Ashi scalp entry sets |
| 3 | PASS | No exchange header. |
| 4 | DONE | Qty = min(2, max(1, round(volume / sma(volume, 70)))) and 100 % of equity stored, not ported. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`volume_f` [2.6, 1.5] x `rmi_len` [30, 14]: **4 trials**; the other settings as written.

## Ambiguities resolved

- The ADX tests and the shared exit id are kept as written (weird case). Bar size from the title (30MIN).
- Volume = broker tick volume. REVERSAL INTENDED. FREQ = "30min".

## FAMILY (proposed, user to confirm)

`FAMILY = "multi_indicator_confluence"`.

## Marks

`trailing_stop_pending`
