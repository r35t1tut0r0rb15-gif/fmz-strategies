"""Sequential count entries with a trailing stop, 1-minute bars: after nine bars in which the close was not under the close four bars back (and the
bar rises), and again on the 13th, 15th and 16th such bar, the strategy goes short; the mirror counts go long (on the 9th, 13th to 16th);
each position carries a trailing stop.
Port of FMZ strategy #435772 "动量TD反转交易策略Momentum-TD-Reversal-Trading-Strategy" (Sequential Up/Down).

FMZ source id: 435772

Source
    https://www.fmz.com/strategy/435772 (PineScript v4, FMZ last modified 2023-12-18 17:40:10).
    Verbatim copy: original_source.md. Read 2026-10-18 (FMZ-C).

Original signal (original_source.md lines 128-211), count 9; overshoots 13, 14, 15, 16; trailing stop 100 points
    priceflip = barssince(src < src[4]);  sellsetup = src > src[4] and priceflip;  sell = sellsetup and barssince(priceflip != 9): priceflip == 9;  overshoots at 13 / 14 / 15 / 16 (the 14 is not used for shorts)
    priceflip1 = barssince(src > src[4]): buy at 9, overshoots 13 / 14 / 15 / 16;  entry Buy on any, Sell on any;  exit(trail_points = 100, trail_offset = na)

Interpretation choices (Pine rules in SURVEY_README.md)
    * barssince(x) is the number of bars since x was last true (0 on the bar it is true). The
      condition "sellsetup and priceflip != 9 earlier" is true exactly when priceflip equals 9 on a
      bar with src above src[4] (and the same for the other counts). The short entry set is
      9, 13, 15 and 16; the long entry set is 9, 13, 14, 15 and 16, as written.
    * Criterion 2: the trailing stop of 100 points is a price-unit trail: ported natively as a percent
      trail from the best high / low (mark trailing_stop): 0.00025 reads 100 points (a 0.1 tick) as 10
      USD on BTC at about 40000, 0.002 a wider trail. strategy.entry reverses: REVERSAL INTENDED. Stop
      module: portfolio_kwargs {} (driver D4). FREQ = "1min" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; trailing stop native.
    2 generic: ADAPT, price-unit trail -> percent trail.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: the trailing-stop inputs quoted in original_sizing.txt.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
REVERSAL INTENDED.

Marks: trailing_stop
"""
import numpy as np
import pandas as pd

NAME = "fmz_435772_sequential_count_entries_trail"
FAMILY = "sequential_count"  # proposed 2026-10-18 (FMZ-C), user to confirm
FREQ = "1min"  # backtest header period: 1m
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "bars_count": [9, 8],
    "trail_pct": [0.00025, 0.002],
}
DEFAULT_PARAMS = {"bars_count": 9, "trail_pct": 0.00025, "lag": 4}


def _resample(raw_1m_df, freq):
    ohlc = raw_1m_df[["open", "high", "low", "close"]]
    bars = ohlc.resample(freq, label="left", closed="left").agg(
        {"open": "first", "high": "max", "low": "min", "close": "last"})
    bars = bars.dropna(how="all")  # an empty period is not a bar; never forward-filled
    if bars.index.tz is None:
        raise ValueError("raw_1m_df must have a tz-aware UTC index")
    return bars


def precompute(raw_1m_df, symbol_key, **params):
    return _resample(raw_1m_df, FREQ)


def _barssince(cond):
    """Pine barssince: bars since cond was last true (0 when true now); NaN before the first true."""
    out = np.full(len(cond), np.nan)
    last = -1
    for i in range(len(cond)):
        if cond[i]:
            last = i
        if last >= 0:
            out[i] = i - last
    return out


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    src = bars_df["close"]
    ref = src.shift(int(p["lag"]))
    up = (src > ref).to_numpy()
    dn = (src < ref).to_numpy()
    pf = _barssince(dn)                       # priceflip: bars since src < src[4]
    pf1 = _barssince(up)                      # priceflip1: bars since src > src[4]
    nb = int(p["bars_count"])
    sell = up & np.isin(pf, [nb, nb + 4, nb + 6, nb + 7])
    buy = dn & np.isin(pf1, [nb, nb + 4, nb + 5, nb + 6, nb + 7])
    ix = bars_df.index
    false = pd.Series(False, index=ix)
    return pd.Series(buy, index=ix), false, pd.Series(sell, index=ix), false.copy()


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    return {"trail": {"type": "percent", "pct": float(p["trail_pct"]), "anchor": "high_low"}}


def portfolio_kwargs(**params):
    return {}
