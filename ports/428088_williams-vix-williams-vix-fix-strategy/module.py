"""Williams Vix Fix long, broker days: after the Vix Fix (distance of the low from the 22-bar highest
close) has been at a spike (above its upper band or 85 % of its 50-bar high) and just eased, a bar with
upward price action that closes above the close 3 bars ago but below the close 14 or 40 bars ago goes
long; a stochastic K crossing above D over 80 closes it.
Port of FMZ strategy #428088 "Williams VIX Fix Strategy" (Vix FIX / StochRSI Strategy).

FMZ source id: 428088

Source
    https://www.fmz.com/strategy/428088 (PineScript v4, FMZ last modified 2023-09-28 15:29:48).
    Verbatim copy: original_source.md. Read 2026-10-16 (FMZ-C).

Original signal (original_source.md lines 180-263), WVF 22, BB 20 x 2, percentile 50 x 0.85, str 3, LB 14 / 40
    wvf = (highest(close, 22) - low) / highest(close, 22) x 100
    filtered = spike[1] and no spike now; filtered_Aggr = spike[1] and spike now (spike = wvf >= upper or >= rangeHigh)
    alert3 = low > low[1] and close > high[1] and close > close[3] and (close < close[40] or close < close[14]) and filtered
    alert4 = close > close[1] and close > open[1] and close > close[3] and (...) and filtered_Aggr
    alert3 or alert4 -> entry long; crossover(k, d) and k > 80 -> close

Interpretation choices (Pine rules in SURVEY_README.md)
    * pyramiding 9 adds are sizing (one unit held). An entry and a close on one bar while long: the
      close wins (stated). The RSI is computed but unused. Long only.
    * Daily bars are broker days (17:00 America/New_York), stamped with their first minute.
    * FREQ = "1D" from the backtest header (period 1d).

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, percent distances, bands, stochastic levels.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: pyramiding 9 and the equity quantity stored in original_sizing.txt.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: DG428088 (3 members, best partner #428627, Jaccard 0.981); ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: broker day (17:00 America/New_York, DST by the zone); no venue-open rule.
Long only.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_428088_williams_vix_fix_long"
FAMILY = "volatility_spike_reversal"  # proposed 2026-10-16 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "pd": [22, 11],
    "ph": [0.85, 0.9],
}
DEFAULT_PARAMS = {"pd": 22, "bbl": 20, "mult": 2.0, "lb": 50, "ph": 0.85, "lt_lb": 40, "mt_lb": 14, "strength": 3,
                  "stoch_len": 14, "smooth_k": 3, "smooth_d": 3, "stoch_ob": 80}


def broker_day(index):
    """Broker day of each timestamp: the session ending 17:00 America/New_York, labelled by its
    end date (as worker A's ports). The desktop binds this name to registry_schema.broker_day."""
    ny = index.tz_convert("America/New_York")
    return (ny + pd.Timedelta(hours=7)).normalize().tz_localize(None)


def precompute(raw_1m_df, symbol_key, **params):
    df = raw_1m_df[["open", "high", "low", "close"]].dropna(how="all")
    if df.index.tz is None:
        raise ValueError("raw_1m_df must have a tz-aware UTC index")
    lab = broker_day(df.index)
    bars = df.groupby(lab).agg({"open": "first", "high": "max", "low": "min", "close": "last"})
    first = pd.Series(df.index, index=df.index).groupby(lab).first()
    bars.index = pd.DatetimeIndex(first.loc[bars.index].values)   # each bar stamped with its first minute
    if bars.index.tz is None:
        bars.index = bars.index.tz_localize("UTC")
    return bars


def _emit(tgt, index):
    prev = np.concatenate(([0], tgt[:-1]))
    le = (tgt == 1) & (prev != 1)
    lx = (prev == 1) & (tgt == 0)
    se = (tgt == -1) & (prev != -1)
    sx = (prev == -1) & (tgt == 0)
    return tuple(pd.Series(a, index=index) for a in (le, lx, se, sx))


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    o, h, lo, c = (bars_df[k] for k in ("open", "high", "low", "close"))
    hc = c.rolling(int(p["pd"])).max()
    wvf = (hc - lo) / hc * 100
    n = int(p["bbl"])
    upper = wvf.rolling(n).mean() + p["mult"] * wvf.rolling(n).std(ddof=0)
    range_high = wvf.rolling(int(p["lb"])).max() * p["ph"]
    spike = (wvf >= upper) | (wvf >= range_high)
    calm = (wvf < upper) & (wvf < range_high)
    spike1 = spike.shift(1, fill_value=False).astype(bool)
    filtered = spike1 & calm
    filtered_aggr = spike1 & ~calm
    st = int(p["strength"])
    base = (c > c.shift(st)) & ((c < c.shift(int(p["lt_lb"]))) | (c < c.shift(int(p["mt_lb"]))))
    a3 = (lo > lo.shift(1)) & (c > h.shift(1)) & base & filtered
    a4 = (c > c.shift(1)) & (c > o.shift(1)) & base & filtered_aggr
    enter = (a3 | a4).to_numpy()
    sl = int(p["stoch_len"])
    ll, hh = lo.rolling(sl).min(), h.rolling(sl).max()
    k = (100 * (c - ll) / (hh - ll)).rolling(int(p["smooth_k"])).mean()
    d = k.rolling(int(p["smooth_d"])).mean()
    close_l = ((k > d) & (k.shift(1) <= d.shift(1)) & (k > p["stoch_ob"])).to_numpy()
    m = len(enter)
    tgt = np.zeros(m, dtype=np.int8)
    pos = 0
    for i in range(m):
        start = pos
        if start == 1 and close_l[i]:
            pos = 0
        if start == 0 and enter[i]:
            pos = 1
        tgt[i] = pos
    return _emit(tgt, bars_df.index)


def portfolio_kwargs(**params):
    return {}
