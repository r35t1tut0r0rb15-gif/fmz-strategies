"""MACD cross-ups below zero on green bars, daily bars, long only, from flat: stop 2 ATR(5) and target 5 ATR(5) from the signal close.
Port of FMZ strategy #448774 "基于MACD信号线交叉与ATR风险管理的优化趋势跟踪策略-Optimized-MACD-Trend-Following-Strategy-with-ATR-based-Risk-Management" (Opt. MACD RM (Optimized MACD Trend-Following Strategy with Risk Management)).

FMZ source id: 448774

Source
    https://www.fmz.com/strategy/448774 (PineScript v5, FMZ last modified 2024-04-18 17:15:00).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 107-147), MACD 12 / 26 / 9; ATR 5, stop x 2, target x 5; risk 2 % (unused)
    crossover(macd, signal) and macd < 0 and close > open and no open trade -> entry Buy, exit(stop = close - 2 atr5, limit = close + 5 atr5)

Interpretation choices (Pine rules in SURVEY_README.md)
    * The bracket is set on the signal bar from its close and ATR(5): sl_stop = 2 ATR / close, tp_stop
      = 5 ATR / close, shifted one bar inside stops() and re-based on the fill; entries only from flat,
      so it is never re-sent inside a trade. Daily stop module: mark coarse_bar_stop. Long only. Stop
      module: portfolio_kwargs {} (driver D4). No sizing code. FREQ = "1D" from the backtest header
      (broker days).

Admission criteria
    1 fits the interface: PASS, bar-close orders; bracket fixed on the signal bar.
    2 generic: PASS, MACD cross-ups below zero with an ATR bracket.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
Long only.

Marks: coarse_bar_stop
"""
import numpy as np
import pandas as pd

NAME = "fmz_448774_macd_cross_below_zero_green_atr_bracket_long"
FAMILY = "macd_cross"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "sl_mult": [2.0, 1.0],
    "tp_mult": [5.0, 3.0],
}
DEFAULT_PARAMS = {"sl_mult": 2.0, "tp_mult": 5.0, "atr_len": 5}


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


def simulate(bars_df, **params):
    o, c = bars_df["open"], bars_df["close"]
    macd = c.ewm(span=12, adjust=False).mean() - c.ewm(span=26, adjust=False).mean()
    sig = macd.ewm(span=9, adjust=False).mean()
    le = (macd > sig) & (macd.shift(1) <= sig.shift(1)) & (macd < 0) & c.shift(1).notna() & (c > o)
    false = pd.Series(False, index=bars_df.index)
    return le, false, false.copy(), false.copy()


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    a = _atr(bars_df, p["atr_len"]) / bars_df["close"]
    return {"sl_stop": (float(p["sl_mult"]) * a).shift(1), "tp_stop": (float(p["tp_mult"]) * a).shift(1)}


def portfolio_kwargs(**params):
    return {}
