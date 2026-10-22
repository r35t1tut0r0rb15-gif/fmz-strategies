"""EMA 9 / 21 crossings with an RSI 14 filter, daily bars: the cross up with RSI under 70 goes long, the cross down with RSI over 30 goes short; reversing. Each trade has a 1 % stop and 2 % target from its signal close.
Port of FMZ strategy #473706 "双均线交叉结合RSI动量优化交易策略-Dual-EMA-Crossover-with-RSI-Momentum-Enhanced-Trading-Strategy" (abo 3llash - EMA + RSI Strategy).

FMZ source id: 473706

Source
    https://www.fmz.com/strategy/473706 (PineScript v5, FMZ last modified 2024-12-02 16:20:01).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 86-130), EMA 9 / 21; RSI 14, 70 / 30; stop 1 %, target 2 % of the signal close; 10 % of equity
    crossover and rsi < 70 -> entry Buy, exit(stop = close x 0.99, limit = close x 1.02);  crossunder and rsi > 30 -> entry Sell, exit(stop = close x 1.01, limit = close x 0.98)

Interpretation choices (Pine rules in SURVEY_README.md)
    * The bracket is sent once, on the signal bar, from its close: sent as fractions of the fill open;
      a level at or through it is marketable and closed one bar late (as #458256). Crossings alternate,
      so no repeat signal re-sends it. REVERSAL INTENDED. Stop module: portfolio_kwargs {} (driver D4).
      Stops on daily bars: mark coarse_bar_stop. The equity share is not ported. FREQ = "1D" from the
      backtest header (broker days).

Admission criteria
    1 fits the interface: PASS, bar-close orders; signal-bar bracket as fractions of the fill.
    2 generic: PASS, EMA crossings with an RSI filter and a bracket.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: percent-of-equity size stored, not ported.
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

NAME = "fmz_473706_ema9_21_cross_rsi_filter_signal_close_bracket_reversal"
FAMILY = "ma_cross"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "sl_pct": [0.01, 0.02],
    "tp_pct": [0.02, 0.04],
}
DEFAULT_PARAMS = {"sl_pct": 0.01, "tp_pct": 0.02}


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
    c = bars_df["close"]
    a, b = c.ewm(span=9, adjust=False).mean(), c.ewm(span=21, adjust=False).mean()
    r = _rsi(c, 14)
    le = (a > b) & (a.shift(1) <= b.shift(1)) & (r < 70)
    se = (a < b) & (a.shift(1) >= b.shift(1)) & (r > 30)
    ks, kt = float(p["sl_pct"]), float(p["tp_pct"])
    lvl = {"l_sl": c * (1 - ks), "l_tp": c * (1 + kt), "s_sl": c * (1 + ks), "s_tp": c * (1 - kt)}
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
