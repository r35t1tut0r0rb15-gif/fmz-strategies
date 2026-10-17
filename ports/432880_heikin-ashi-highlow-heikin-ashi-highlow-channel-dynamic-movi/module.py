"""Heikin Ashi high / low channel, long only, no bar size in the source: the Heikin Ashi close above the SMA 5 of the Heikin
Ashi highs goes long; below the SMA 5 of the Heikin Ashi lows closes it.
Port of FMZ strategy #432880 "Heikin-Ashi-HighLow通道动态均线交易策略Heikin-Ashi-HighLow-Channel-Dynamic-Moving-Average-Trading-Strategy" (Hi-Lo Channel Strategy).

FMZ source id: 432880

Source
    https://www.fmz.com/strategy/432880 (PineScript v4, FMZ last modified 2023-11-22 14:43:58).
    Verbatim copy: original_source.md. Read 2026-10-17 (FMZ-C).

Original signal (original_source.md lines 115-149), SMA 5 of HA highs, SMA 5 of HA lows, Heikin Ashi values on
    ha_c > sma(ha_h, 5) -> entry long ("Buy", 100 = long);  ha_c < sma(ha_l, 5) -> close long

Interpretation choices (Pine rules in SURVEY_README.md)
    * The source has no backtest header and names no bar size: FREQ = "bar_size_pending" (rule 1).
      precompute builds the bars with the house bar_sizes.build_bars(raw_1m_df, params["bar_size"]);
      the driver supplies bar_size (never in GRID / DEFAULT_PARAMS).
    * The Heikin Ashi candles are the chart's own (security of the heikinashi ticker on the same
      timeframe): close = ohlc4, open = the average of the previous HA open and close (seeded with
      (open + close) / 2), high / low the extremes with them. strategy.entry("Buy", 100): the second
      argument is the direction, 100 reads as true (long).
    * Long only; Opposite entries cannot occur.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, Heikin Ashi channel.
    3 crypto-exchange-only: no.
    4 signals only: 100 % of equity stored in original_sizing.txt.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
Long only. Opposite entries cannot occur.

Marks: bar_size_pending
"""
import numpy as np
import pandas as pd

NAME = "fmz_432880_heikin_ashi_hilo_channel_long"
FAMILY = "heikin_ashi_trend"  # proposed 2026-10-17 (FMZ-C), user to confirm
FREQ = "bar_size_pending"
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "len_h": [5, 10],
    "len_l": [5, 10],
}
DEFAULT_PARAMS = {"len_h": 5, "len_l": 5}


def precompute(raw_1m_df, symbol_key, **params):
    import bar_sizes                      # the house builder (mining\bar_sizes.py), on the desktop's path
    return bar_sizes.build_bars(raw_1m_df, params["bar_size"])


def _ha(o, h, lo, c):
    hc = (o + h + lo + c) / 4
    ho = np.full(len(c), np.nan)
    for i in range(len(c)):
        ho[i] = (o[i] + c[i]) / 2 if i == 0 or np.isnan(ho[i - 1]) else (ho[i - 1] + hc[i - 1]) / 2
    hh = np.maximum(h, np.maximum(ho, hc))
    hl = np.minimum(lo, np.minimum(ho, hc))
    return ho, hh, hl, hc


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    o, h, lo, c = (bars_df[k].to_numpy(dtype=float) for k in ("open", "high", "low", "close"))
    _, hh, hl, hc = _ha(o, h, lo, c)
    idx = bars_df.index
    mah = pd.Series(hh, index=idx).rolling(int(p["len_h"])).mean()
    mal = pd.Series(hl, index=idx).rolling(int(p["len_l"])).mean()
    hcs = pd.Series(hc, index=idx)
    le = (hcs > mah).astype(bool)
    lx = (hcs < mal).astype(bool)
    false = pd.Series(False, index=idx)
    return le, lx, false, false.copy()


def portfolio_kwargs(**params):
    return {}
