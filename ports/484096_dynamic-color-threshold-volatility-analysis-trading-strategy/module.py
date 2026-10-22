"""Heikin-Ashi-style colour changes with a 1 % body threshold, 2-day bars: a red-to-green change goes long, a green-to-red change goes short, each with a 20-tick stop and a 40-tick target from the signal close read as fractions; the opposite change closes; reversing.
Port of FMZ strategy #484096 "Dynamic Color Threshold Volatility Analysis Trading Strategy" (Color Code Overlay Strategy).

FMZ source id: 484096

Source
    https://www.fmz.com/strategy/484096 (PineScript v5, FMZ last modified 2025-02-28 09:59:24).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 250-339), colour-code candles (ohlc4 close, averaged open); threshold 1 % of the candle range; stop 20 pips; target 40 pips (ticks); trade type Both
    cc_close = ohlc4;  cc_open = na(cc_open[1]) ? (open + close) / 2 : (cc_open[1] + cc_close[1]) / 2;  range from max / min of high, low, cc_open, cc_close
    red-to-green with |body| > 1 % of range -> entry Long + exit(stop = close - 20 ticks, limit = close + 40 ticks);  green-to-red -> close Long
    green-to-red -> entry Short + mirror;  red-to-green -> close Short

Interpretation choices (Pine rules in SURVEY_README.md)
    * The trade-type menu keeps its default (Both). The colour changes alternate, so each change closes
      one side and enters the other: REVERSAL INTENDED.
    * Criterion 2: 20 / 40 ticks on the header's ETH_USDT (tick 0.01, about 3000 USDT) are read as
      6.667e-05 / 1.333e-04 of the price (as #458242 at the header's prices); the levels are fixed at the
      signal close and sent as fractions of the fill open (a level at or through it is marketable and
      closed one bar late, as #458256). Stop module: portfolio_kwargs {} (driver D4). Stops on bars
      longer than 1 hour: mark coarse_bar_stop. No sizing code. Bars are blocks of two broker days (17:00
      America/New_York) counted from 1970-01-01, stamped with their first minute. FREQ = "2D" from the
      backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; tick bracket as fractions of the fill.
    2 generic: ADAPT, tick bracket read as fractions at ETH 3000.
    3 crypto-exchange-only: no (futures exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: two-broker-day blocks (17:00 America/New_York, DST by the zone).
REVERSAL INTENDED.

Marks: coarse_bar_stop
"""
import numpy as np
import pandas as pd

NAME = "fmz_484096_colour_code_candle_change_tick_bracket_reversal"
FAMILY = "heikin_ashi_trend"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "2D"  # backtest header period: 2d (two broker days)
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "stop_frac": [6.667e-05, 0.01],
    "threshold_percent": [1.0, 5.0],
}
DEFAULT_PARAMS = {"stop_frac": 6.667e-05, "threshold_percent": 1.0, "tp_mult": 2.0, "days": 2}


def broker_day(index):
    """Broker day of each timestamp: the session ending 17:00 America/New_York, labelled by its
    end date (as worker A's ports). The desktop binds this name to registry_schema.broker_day."""
    ny = index.tz_convert("America/New_York")
    return (ny + pd.Timedelta(hours=7)).normalize().tz_localize(None)


def _multiday(raw_1m_df, days):
    """Blocks of `days` broker days counted from 1970-01-01, each stamped with its first minute."""
    df = raw_1m_df[["open", "high", "low", "close"]].dropna(how="all")
    if df.index.tz is None:
        raise ValueError("raw_1m_df must have a tz-aware UTC index")
    key = np.asarray((broker_day(df.index) - pd.Timestamp("1970-01-01")).days // days)
    bars = df.groupby(key).agg({"open": "first", "high": "max", "low": "min", "close": "last"})
    first = pd.Series(df.index, index=df.index).groupby(key).first()
    bars.index = pd.DatetimeIndex(first.loc[bars.index].values)
    if bars.index.tz is None:
        bars.index = bars.index.tz_localize("UTC")
    return bars


def precompute(raw_1m_df, symbol_key, **params):
    p = {**DEFAULT_PARAMS, **params}
    return _multiday(raw_1m_df, int(p["days"]))


def _signals(bars_df, p):
    o, h, lo, c = bars_df["open"], bars_df["high"], bars_df["low"], bars_df["close"]
    cc = ((o + h + lo + c) / 4).to_numpy(dtype=float)
    ov, cv = o.to_numpy(dtype=float), c.to_numpy(dtype=float)
    m = len(cv)
    co = np.full(m, np.nan)
    for i in range(m):
        co[i] = (ov[i] + cv[i]) / 2 if (i == 0 or np.isnan(co[i - 1])) else (co[i - 1] + cc[i - 1]) / 2
    cco, ccc = pd.Series(co, index=c.index), pd.Series(cc, index=c.index)
    hi = np.maximum(h, np.maximum(cco, ccc))
    lw = np.minimum(lo, np.minimum(cco, ccc))
    thr = float(p["threshold_percent"]) / 100 * (hi - lw)
    bull = ccc > cco
    was = bull.shift(1, fill_value=False)
    big = (ccc - cco).abs() > thr
    le = ~was & bull & big
    se = was & ~bull & big
    a = float(p["stop_frac"])
    b = a * float(p["tp_mult"])
    lvl = {"l_sl": c * (1 - a), "l_tp": c * (1 + b), "s_sl": c * (1 + a), "s_tp": c * (1 - b)}
    return le, se, lvl


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    le, se, lvl = _signals(bars_df, p)
    o = bars_df["open"]
    lf, sf = le.shift(1, fill_value=False), se.shift(1, fill_value=False)
    l_thr = (lvl["l_sl"].shift(1) >= o) | (lvl["l_tp"].shift(1) <= o)    # marketable at the fill
    s_thr = (lvl["s_sl"].shift(1) <= o) | (lvl["s_tp"].shift(1) >= o)
    return le, lf & l_thr & ~le & ~se, se, sf & s_thr & ~se & ~le


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    le, se, lvl = _signals(bars_df, p)
    o = bars_df["open"]
    lf = le.shift(1, fill_value=False)
    l_sl, l_tp = 1 - lvl["l_sl"].shift(1) / o, lvl["l_tp"].shift(1) / o - 1
    s_sl, s_tp = lvl["s_sl"].shift(1) / o - 1, 1 - lvl["s_tp"].shift(1) / o
    sl = l_sl.where(lf, s_sl)
    tp = l_tp.where(lf, s_tp)
    return {"sl_stop": sl.where(sl > 0), "tp_stop": tp.where(tp > 0)}


def portfolio_kwargs(**params):
    return {}
