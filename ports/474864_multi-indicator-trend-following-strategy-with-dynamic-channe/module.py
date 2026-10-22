"""G-Channel state against the EMA 50, alternating signals, daily bars: when the channel state is bullish and the close under the EMA 50 (and the last signal was not a buy) it goes long, when bearish and the close over it (and the last was not a sell) it goes short; each trade has a 2 ATR stop and 4 ATR target from its signal close; reversing.
Port of FMZ strategy #474864 "Multi Indicator Trend Following Strategy with Dynamic Channel and Moving Average Trading System" (G-EMA-ATR).

FMZ source id: 474864

Source
    https://www.fmz.com/strategy/474864 (PineScript v5, FMZ last modified 2024-12-12 15:58:57).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 98-166), G-Channel 100; EMA 50; ATR 14: stop 2 x, target 4 x
    a := max(src, nz(a[1])) - nz(a[1] - b[1]) / 100;  b := min(src, nz(b[1])) + nz(a[1] - b[1]) / 100;  crossup = b[1] < close[1] and b > close;  crossdn = a[1] < close[1] and a > close;  bullish = barssince(crossdn) <= barssince(crossup);  bullish and close < ema50 and not lastBuy -> entry Buy + exit(stop = close - 2 atr, limit = close + 4 atr);  mirror -> entry Sell + exit

Interpretation choices (Pine rules in SURVEY_README.md)
    * The channel is a recursion from nz seeds of 0 (a loop), and the cross tests are as written (b rising
      through the close, a rising through the close). barssince is na before the first cross, and a
      comparison with na is false. The last-signal flags make the signals alternate (a loop), so no
      repeat signal re-sends a bracket. The bracket is sent on the signal bar from its close: sent as
      fractions of the fill open; a level at or through it is marketable and closed one bar late (as
      #458256). REVERSAL INTENDED. Stop module: portfolio_kwargs {} (driver D4). Stops on daily bars:
      mark coarse_bar_stop. No sizing code. FREQ = "1D" from the backtest header (broker days).

Admission criteria
    1 fits the interface: PASS, bar-close orders; signal-bar ATR bracket as fractions of the fill.
    2 generic: PASS, G-Channel state against an EMA with alternating signals and a bracket.
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

NAME = "fmz_474864_g_channel100_ema50_alternating_atr_bracket_reversal"
FAMILY = "volatility_channel_breakout"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "length": [100, 50],
    "ema_length": [50, 100],
}
DEFAULT_PARAMS = {"length": 100, "ema_length": 50, "atr_length": 14}


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


def _atr(bars_df, n):
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    pc = c.shift(1)
    tr = pd.concat([h - lo, (h - pc).abs(), (lo - pc).abs()], axis=1).max(axis=1)
    return _rma(tr, int(n))


def _barssince(k):
    out = np.full(len(k), np.nan)
    last = -1
    for i in range(len(k)):
        if k[i]:
            last = i
        if last >= 0:
            out[i] = i - last
    return out


def _signals(bars_df, p):
    c = bars_df["close"]
    cv = c.to_numpy(dtype=float)
    n = float(p["length"])
    av, bv = np.zeros(len(cv)), np.zeros(len(cv))
    a1 = b1 = 0.0
    for i in range(len(cv)):
        a = max(cv[i], a1) - (a1 - b1) / n
        b = min(cv[i], b1) + (a1 - b1) / n
        av[i], bv[i] = a, b
        a1, b1 = a, b
    cu = np.zeros(len(cv), dtype=bool)
    cd = np.zeros(len(cv), dtype=bool)
    cu[1:] = (bv[:-1] < cv[:-1]) & (bv[1:] > cv[1:])
    cd[1:] = (av[:-1] < cv[:-1]) & (av[1:] > cv[1:])
    bull = _barssince(cd) <= _barssince(cu)      # na compares false
    e = c.ewm(span=int(p["ema_length"]), adjust=False).mean().to_numpy(dtype=float)
    buy, sell = bull & (cv < e), ~bull & (cv > e)
    le, se = np.zeros(len(cv), dtype=bool), np.zeros(len(cv), dtype=bool)
    lb = ls = False
    for i in range(len(cv)):
        if buy[i] and not lb:
            le[i], lb, ls = True, True, False
        if sell[i] and not ls:
            se[i], ls, lb = True, True, False
    ix = bars_df.index
    atr = _atr(bars_df, p["atr_length"])
    lvl = {"l_sl": c - 2 * atr, "l_tp": c + 4 * atr, "s_sl": c + 2 * atr, "s_tp": c - 4 * atr}
    return pd.Series(le, index=ix), pd.Series(se, index=ix), lvl


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
