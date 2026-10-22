"""Bollinger 20 / 2 breakouts with an RSI 50 filter, daily bars: a close over the upper band with RSI over 50 goes long, under the lower band with RSI under 50 goes short; reversing. Each trade has a 2 % stop and a 4 % target (risk-reward 2) from its signal close.
Port of FMZ strategy #474075 "基于布林带和RSI的多维度动态突破交易系统-Multi-Dimensional-Dynamic-Breakout-Trading-System-Based-on-Bollinger-Bands-and-RSI" (Bollinger Breakout Strategy with Direction Control).

FMZ source id: 474075

Source
    https://www.fmz.com/strategy/474075 (PineScript v5, FMZ last modified 2024-12-05 17:32:23).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 98-158), BB 20, 2 sd; RSI 14, midline 50; stop 2 %, target 2 % x 2 of the signal close; direction Both
    close > upper and rsi > 50 -> entry_price_long := close, entry Long;  close < lower and rsi < 50 -> entry_price_short := close, entry Short;  long: exit(stop = entry x 0.98, limit = entry x 1.04);  short mirror

Interpretation choices (Pine rules in SURVEY_README.md)
    * The levels come from the signal bar's close (stored on every signal bar, also on repeats while
      the trade is open): the opening signal's levels are ported, sent as fractions of the fill open (a
      level at or through it is marketable and closed one bar late, as #458256); the re-stored levels of
      repeat signals are not followed (as #434428, mark trailing_stop_pending). Direction "Both"
      (default). REVERSAL INTENDED. Stop module: portfolio_kwargs {} (driver D4). Stops on daily bars:
      mark coarse_bar_stop. No sizing code. FREQ = "1D" from the backtest header (broker days).

Admission criteria
    1 fits the interface: PASS, bar-close orders; signal-bar bracket as fractions of the fill.
    2 generic: PASS, band breakouts with an RSI filter and a bracket.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (8 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
REVERSAL INTENDED.

Marks: coarse_bar_stop, trailing_stop_pending
"""
import numpy as np
import pandas as pd

NAME = "fmz_474075_bb20_breakout_rsi50_signal_close_bracket_reversal"
FAMILY = "bollinger_breakout"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "length": [20, 50],
    "mult": [2.0, 1.5],
    "rr": [2.0, 1.0],
}
DEFAULT_PARAMS = {"length": 20, "mult": 2.0, "rr": 2.0, "stop_pct": 0.02}


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
    n = int(p["length"])
    basis = c.rolling(n).mean()
    dev = float(p["mult"]) * c.rolling(n).std(ddof=0)
    r = _rsi(c, 14)
    le = (c > basis + dev) & (r > 50)
    se = (c < basis - dev) & (r < 50)
    sp = float(p["stop_pct"])
    tp = sp * float(p["rr"])
    lvl = {"l_sl": c * (1 - sp), "l_tp": c * (1 + tp), "s_sl": c * (1 + sp), "s_tp": c * (1 - tp)}
    return le, se, lvl


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    le, se, lvl = _signals(bars_df, p)
    o = bars_df["open"]
    lf = le.shift(1, fill_value=False)
    sf = se.shift(1, fill_value=False)
    l_thr = (lvl["l_sl"].shift(1) >= o) | (lvl["l_tp"].shift(1) <= o)    # marketable at the fill
    s_thr = (lvl["s_sl"].shift(1) <= o) | (lvl["s_tp"].shift(1) >= o)
    return le, lf & l_thr & ~se & ~le, se, sf & s_thr & ~le & ~se


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
