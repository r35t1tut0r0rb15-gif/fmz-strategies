"""EMA 9 / 55 crossings with RSI 14 confirmation, daily bars: the cross up with RSI over 60 goes long, the cross down with RSI under 40 goes short; reversing. A long's stop is 1 % under its signal bar's high and its first target 1.6 % over it; a short's stop 1 % over the signal low, its first target 1.6 % under it.
Port of FMZ strategy #474038 "五均线RSI趋势跟踪动态通道交易系统-Five-EMA-RSI-Trend-Following-Dynamic-Channel-Trading-System" (EMA RSI Donchian Strategy).

FMZ source id: 474038

Source
    https://www.fmz.com/strategy/474038 (PineScript v5, FMZ last modified 2024-12-05 15:15:28).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 90-183), EMA 9 / 21 / 55 / 89 / 144; RSI 14, 60 / 40; Donchian 21 / 74 (plotted); SL / TP1 / TP2 from the signal bar's high / low
    crossover(ema9, ema55) and rsi > 60 -> sl := high x 0.99, tp1 := sl x 1.02618, tp2 := sl x 1.036185, entry Long;  short mirror (sl := low x 1.01, tp1 := sl x 0.97382, tp2 := tp1 x 0.96381);  every bar once set: exit(limit = tp1), exit(limit = tp2), exit(stop = sl)

Interpretation choices (Pine rules in SURVEY_README.md)
    * The levels are stored on each signal bar (var) and the three full-size exits are re-sent every
      bar with them, so each trade's bracket is its signal bar's: the stop and the nearer target TP1
      (TP2 is farther and can only fill after TP1 has closed the trade). Sent as fractions of the fill
      open; a level at or through it (a long's stop is over the close when the bar closed more than 1 %
      under its high) is marketable and closed one bar late (as #458256). Crossings alternate, so no
      repeat signal re-sets them. The other EMAs and the Donchian channels feed no order. REVERSAL
      INTENDED. Stop module: portfolio_kwargs {} (driver D4). Stops on daily bars: mark coarse_bar_stop.
      No sizing code. FREQ = "1D" from the backtest header (broker days).

Admission criteria
    1 fits the interface: PASS, bar-close orders; signal-bar bracket as fractions of the fill.
    2 generic: PASS, EMA crossings with RSI confirmation and a signal-bar bracket.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
REVERSAL INTENDED.

Marks: coarse_bar_stop
"""
import numpy as np
import pandas as pd

NAME = "fmz_474038_ema9_55_cross_rsi60_40_signal_bar_bracket_reversal"
FAMILY = "ma_cross"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "fast": [9, 5],
    "slow": [55, 100],
}
DEFAULT_PARAMS = {"fast": 9, "slow": 55}


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
    return 100 - 100 / (1 + up / dn)


def _signals(bars_df, p):
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    a = c.ewm(span=int(p["fast"]), adjust=False).mean()
    b = c.ewm(span=int(p["slow"]), adjust=False).mean()
    r = _rsi(c, 14)
    le = (a > b) & (a.shift(1) <= b.shift(1)) & (r > 60)
    se = (a < b) & (a.shift(1) >= b.shift(1)) & (r < 40)
    l_sl, s_sl = h * 0.99, lo * 1.01
    lvl = {"l_sl": l_sl, "l_tp": l_sl * 1.02618, "s_sl": s_sl, "s_tp": s_sl * 0.97382}
    return le, se, lvl


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    le, se, lvl = _signals(bars_df, p)
    o = bars_df["open"]
    lf = le.shift(1, fill_value=False)
    sf = se.shift(1, fill_value=False)
    l_thr = (lvl["l_sl"].shift(1) >= o) | (lvl["l_tp"].shift(1) <= o)    # marketable at the fill
    s_thr = (lvl["s_sl"].shift(1) <= o) | (lvl["s_tp"].shift(1) >= o)
    return le, lf & l_thr & ~se, se, sf & s_thr & ~le


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    le, se, lvl = _signals(bars_df, p)
    o = bars_df["open"]
    lf = le.shift(1, fill_value=False)
    sl_f = (1 - lvl["l_sl"].shift(1) / o).where(lf, lvl["s_sl"].shift(1) / o - 1)
    tp_f = (lvl["l_tp"].shift(1) / o - 1).where(lf, 1 - lvl["s_tp"].shift(1) / o)
    return {"sl_stop": sl_f.where(sl_f > 0), "tp_stop": tp_f.where(tp_f > 0)}


def portfolio_kwargs(**params):
    return {}
