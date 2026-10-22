"""RSI 14 crossings of 30 / 70, broker days: RSI up through 30 goes long with the 10-bar low as stop and a 2R target, RSI down through 70 goes short with the 10-bar high as stop and a 2R target, all from the signal close; reversing.
Port of FMZ strategy #483096 "RSI超买超卖交叉结合布林带动态止盈止损策略-RSI-Overbought-Oversold-Crossover-with-Bollinger-Bands-Dynamic-Stop-Loss-Strategy" (RSI Oversold Crossover Strategy).

FMZ source id: 483096

Source
    https://www.fmz.com/strategy/483096 (PineScript v5, FMZ last modified 2025-02-21 13:29:30).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 113-153), RSI 14 / 70 / 30; swing 10 bars; RR 2; MPL 2.0 notice (humblehustle)
    crossover(rsi, 30) -> entry Long + exit(stop = lowest(low, 10), limit = close + 2 (close - stop))
    crossunder(rsi, 70) -> entry Short + exit(stop = highest(high, 10), limit = close - 2 (stop - close))

Interpretation choices (Pine rules in SURVEY_README.md)
    * The swing levels include the signal bar, as written. The levels are fixed at the signal bar and sent
      as fractions of the fill open (a level at or through it is marketable and closed one bar late, as
      #458256). A repeat signal while held re-sends the bracket; stops() keeps the first, so the repeat
      case is marked trailing_stop_pending (as #434428). An entry on the other side reverses (REVERSAL
      INTENDED). Stop module: portfolio_kwargs {} (driver D4). Stops on daily bars: mark coarse_bar_stop.
      No sizing code. The MPL 2.0 notice is kept with the verbatim copy (ported, stated). Daily bars are
      broker days (17:00 America/New_York), stamped with their first minute. FREQ = "1D" from the backtest
      header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; swing bracket as fractions of the fill.
    2 generic: PASS, RSI level crossings with swing brackets.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: broker day (17:00 America/New_York, DST by the zone); no venue-open rule.
REVERSAL INTENDED.

Marks: coarse_bar_stop, trailing_stop_pending
"""
import numpy as np
import pandas as pd

NAME = "fmz_483096_rsi14_30_70_cross_swing10_stop_2r_reversal"
FAMILY = "rsi_oscillator"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "rsi_length": [14, 7],
    "swing_bars": [10, 20],
}
DEFAULT_PARAMS = {"rsi_length": 14, "swing_bars": 10, "rsi_ob": 70, "rsi_os": 30, "rr": 2.0}


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


def _rma(x, n):
    """Wilder smoothing as Pine's rma: SMA seed over the first n valid values, then recursive."""
    v = x.to_numpy(dtype=float)
    out = np.full(v.shape, np.nan)
    valid = np.flatnonzero(~np.isnan(v))
    if len(valid) >= n:
        s = valid[0]
        out[s + n - 1] = v[s:s + n].mean()
        for i in range(s + n, len(v)):
            out[i] = (out[i - 1] * (n - 1) + v[i]) / n
    return pd.Series(out, index=x.index)


def _rsi(c, n):
    d = c.diff()
    up, dn = _rma(d.clip(lower=0), n), _rma((-d).clip(lower=0), n)
    r = 100 - 100 / (1 + up / dn)
    r = r.where(dn != 0, 100.0).where(up != 0, 0.0)
    return r.where(up.notna() & dn.notna())


def _signals(bars_df, p):
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    r = _rsi(c, int(p["rsi_length"]))
    os_, ob = float(p["rsi_os"]), float(p["rsi_ob"])
    le = (r > os_) & (r.shift(1) <= os_)
    se = (r < ob) & (r.shift(1) >= ob)
    n, rr = int(p["swing_bars"]), float(p["rr"])
    ls, ss = lo.rolling(n).min(), h.rolling(n).max()
    lvl = {"l_sl": ls, "l_tp": c + (c - ls) * rr, "s_sl": ss, "s_tp": c - (ss - c) * rr}
    return le & ~se, se, lvl


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
