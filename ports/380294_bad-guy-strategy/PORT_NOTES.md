# #380294 Bad guy strategy -> `fmz_380294_adx_mn22_range_filter_sar_volume_state_machine_anchor_bracket_reversal`

- FMZ source id: 380294 (lineage).
- Source: https://www.fmz.com/strategy/380294 (PineScript v4, author Zer3192, FMZ last
  modified 2022-08-29 20:51:48). Verbatim here as `original_source.md`. Read 2026-10-23 (FMZ-C).
- Status: PORTED (batch V4). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; percent bracket from the script's anchor |
| 2 | PASS | ADX / range filter / SAR / volume confluence with a re-arming state machine |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | 100 % of equity, capital 10000, commission 0.04 % and a risk input stored, not ported. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`tp_l` [0.007, 0.012] x `sl` [0.05, 0.03]: **4 trials**; TP_S 0.9 %, the other settings as written.

## Ambiguities resolved

- The script's state machine and anchors are kept as written; the bracket uses the fill bar's anchor.
- Volume = broker tick volume. REVERSAL INTENDED. FREQ = "4h".

## FAMILY (proposed, user to confirm)

`FAMILY = "multi_indicator_confluence"`.

## Marks

`trailing_stop_pending, coarse_bar_stop`
