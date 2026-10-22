"""A Granville close crossing over the EMA 20, then a first MACD 12 / 26 / 9 golden cross, then MACD rising above its value at that cross, then a later golden cross, broker days, long only: the last cross buys with its stop at the Granville bar's low and a target 1.618 Granville ranges over the signal close.
Port of FMZ strategy #482803 "基于Granville与MACD多重信号确认的趋势跟踪交易策略-Trend-Following-Trading-Strategy-Based-on-Granville-and-MACD-Multiple-Signal-Confirmation" (Granville + MACD Strategy).

FMZ source id: 482803

Source
    https://www.fmz.com/strategy/482803 (PineScript v5, FMZ last modified 2025-02-27 17:46:54).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 98-170), EMA 20; MACD 12 / 26 / 9; TP 1.618 x the reversal bar's range; SL its low; 10 % of equity, capital 100000
    crossover(close, ema20) -> granvilleDone, low / range stored, MACD states reset;  first crossover(macd, signal) -> golden cross bar and MACD stored;  macd > stored -> breakout
    granvilleDone and golden cross and breakout and bar > golden cross bar and crossover(macd, signal) -> entry Long + exit(stop = granville low, limit = close + 1.618 range); states reset

Interpretation choices (Pine rules in SURVEY_README.md)
    * The state machine is kept as written (a new Granville crossing restarts it). The levels are fixed at
      the signal bar and sent as fractions of the fill open (a level at or through it is marketable and
      closed one bar late, as #458256). A new sequence can complete while the long is held, re-sending the
      bracket; stops() keeps the first, so the repeat case is marked trailing_stop_pending (as #434428).
      Long only. Stop module: portfolio_kwargs {} (driver D4). Stops on daily bars: mark coarse_bar_stop.
      The 10 % of equity size and capital are sizing. Daily bars are broker days (17:00 America/New_York),
      stamped with their first minute. FREQ = "1D" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; reversal-bar bracket as fractions of the fill.
    2 generic: PASS, Granville / MACD sequence with a range target.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: 10 % of equity and capital stored, not ported.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: broker day (17:00 America/New_York, DST by the zone); no venue-open rule.
Long only.

Marks: coarse_bar_stop, trailing_stop_pending
"""
import numpy as np
import pandas as pd

NAME = "fmz_482803_granville_ema20_macd_gc_breakout_recross_range_bracket_long"
FAMILY = "macd_cross"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "ema_period": [20, 50],
    "tp_mult": [1.618, 2.618],
}
DEFAULT_PARAMS = {"ema_period": 20, "tp_mult": 1.618, "fast_len": 12, "slow_len": 26, "signal_len": 9}


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


def _signals(bars_df, p):
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]

    def ema(x, n):
        return x.ewm(span=int(n), adjust=False).mean()

    e = ema(c, p["ema_period"])
    macd = ema(c, p["fast_len"]) - ema(c, p["slow_len"])
    sig = ema(macd, p["signal_len"])
    grev = ((c > e) & (c.shift(1) <= e.shift(1))).to_numpy()
    mx = ((macd > sig) & (macd.shift(1) <= sig.shift(1))).to_numpy()
    mv, hv, lv, cv = (x.to_numpy(dtype=float) for x in (macd, h, lo, c))
    k = float(p["tp_mult"])
    m = len(cv)
    le = np.zeros(m, dtype=bool)
    l_sl, l_tp = np.full(m, np.nan), np.full(m, np.nan)
    gd = gc = bo = False
    gl = gr = imh = np.nan
    gcb = -1
    for i in range(m):
        if grev[i]:
            gd, gl, gr = True, lv[i], hv[i] - lv[i]
            gc = bo = False
            imh, gcb = np.nan, -1
        if gd and not gc and mx[i]:
            gc, gcb, imh = True, i, mv[i]
        if gc and not bo and mv[i] > imh:
            bo = True
        if gd and gc and bo and i > gcb and mx[i]:
            le[i] = True
            l_sl[i], l_tp[i] = gl, cv[i] + gr * k
            gd = gc = bo = False
            imh, gcb = np.nan, -1
    idx = c.index
    return pd.Series(le, index=idx), {"l_sl": pd.Series(l_sl, index=idx), "l_tp": pd.Series(l_tp, index=idx)}


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    le, lvl = _signals(bars_df, p)
    o = bars_df["open"]
    lf = le.shift(1, fill_value=False)
    l_thr = (lvl["l_sl"].shift(1) >= o) | (lvl["l_tp"].shift(1) <= o)    # marketable at the fill
    false = pd.Series(False, index=o.index)
    return le, lf & l_thr & ~le, false, false.copy()


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    le, lvl = _signals(bars_df, p)
    o = bars_df["open"]
    sl_f = 1 - lvl["l_sl"].shift(1) / o
    tp_f = lvl["l_tp"].shift(1) / o - 1
    return {"sl_stop": sl_f.where(sl_f > 0), "tp_stop": tp_f.where(tp_f > 0)}


def portfolio_kwargs(**params):
    return {}
