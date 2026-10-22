"""EMA 9 / 21 crossings with an RSI 14 filter, daily bars: the cross up with RSI under 70 goes long, the cross down with RSI over 30 goes short; reversing. Each trade has a 2 ATR stop and 4 ATR target from its signal close.
Port of FMZ strategy #474052 "动态止损倍数多周期RSI趋势跟踪策略-Dynamic-Stop-Loss-Multi-Period-RSI-Trend-Following-Strategy" (Aggressive Scalper Strategy).

FMZ source id: 474052

Source
    https://www.fmz.com/strategy/474052 (PineScript v5, FMZ last modified 2024-12-05 16:25:17).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 90-149), EMA 9 / 21; RSI 14; ATR 14: target 4 x, stop 2 x; size from a typed account balance
    crossover and rsi < 70 -> entry Long (qty), exit(limit = close + 4 atr, stop = close - 2 atr);  crossunder and rsi > 30 -> entry Short, exit(limit = close - 4 atr, stop = close + 2 atr)

Interpretation choices (Pine rules in SURVEY_README.md)
    * The bracket is sent once, on the signal bar, from its close and ATR: sent as fractions of the
      fill open; a level at or through it is marketable and closed one bar late (as #458256). Crossings
      alternate, so no repeat signal re-sends it. The ATR multiplier input (1.5) feeds nothing; the
      size from the typed balance and leverage is not ported. REVERSAL INTENDED. Stop module:
      portfolio_kwargs {} (driver D4). Stops on daily bars: mark coarse_bar_stop. FREQ = "1D" from the
      backtest header (broker days).

Admission criteria
    1 fits the interface: PASS, bar-close orders; signal-bar ATR bracket as fractions of the fill.
    2 generic: PASS, EMA crossings with an RSI filter and an ATR bracket.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: size from a typed balance stored, not ported.
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

NAME = "fmz_474052_ema9_21_cross_rsi_atr_bracket_2_4_reversal"
FAMILY = "ma_cross"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "tp_mult": [4, 2],
    "sl_mult": [2, 1],
}
DEFAULT_PARAMS = {"tp_mult": 4, "sl_mult": 2}


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


def _atr(bars_df, n):
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    pc = c.shift(1)
    tr = pd.concat([h - lo, (h - pc).abs(), (lo - pc).abs()], axis=1).max(axis=1)
    return _rma(tr, int(n))


def _signals(bars_df, p):
    c = bars_df["close"]
    a, b = c.ewm(span=9, adjust=False).mean(), c.ewm(span=21, adjust=False).mean()
    r = _rsi(c, 14)
    le = (a > b) & (a.shift(1) <= b.shift(1)) & (r < 70)
    se = (a < b) & (a.shift(1) >= b.shift(1)) & (r > 30)
    atr = _atr(bars_df, 14)
    kt, ks = float(p["tp_mult"]), float(p["sl_mult"])
    lvl = {"l_sl": c - ks * atr, "l_tp": c + kt * atr, "s_sl": c + ks * atr, "s_tp": c - kt * atr}
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
