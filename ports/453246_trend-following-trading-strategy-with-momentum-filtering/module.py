"""MACD 12 / 26 / 9 crossings with an RSI 14 filter, daily bars: the cross up with the RSI over 50 goes long, the cross down with the RSI under 50 goes short; reversing. The stop re-sent every bar from the 10-bar close extreme is not ported (pending).
Port of FMZ strategy #453246 "Trend Following Trading Strategy with Momentum Filtering" (Trend-Following Strategy with MACD and RSI Filter).

FMZ source id: 453246

Source
    https://www.fmz.com/strategy/453246 (PineScript v5, FMZ last modified 2024-06-03 11:23:02).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 93-141), MACD 12 / 26 / 9; RSI 14 vs 50; stops highest(close, 10)[1] x 0.99 / lowest(close, 10)[1] x 1.01 every bar
    crossover(macd, signal) and rsi > 50 -> entry Long;  crossunder and rsi < 50 -> entry Short
    every bar: exit(Long, stop = highest(close, 10)[1] x 0.99);  exit(Short, stop = lowest(close, 10)[1] x 1.01)

Interpretation choices (Pine rules in SURVEY_README.md)
    * The stops are re-sent on every bar from the moving 10-bar close extreme, so they rise and fall
      with the window and can sit on either side of the price; stops() cannot express this: they are
      not ported and the module gets the mark trailing_stop_pending (as #438034); positions end at the
      opposite entry. The SMA 12 / 26 are computed but unused. REVERSAL INTENDED. No sizing code.
      FREQ = "1D" from the backtest header (broker days).

Admission criteria
    1 fits the interface: PASS, bar-close orders; the moving stops pending (mark).
    2 generic: PASS, MACD crossings with an RSI filter.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (8 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
REVERSAL INTENDED.

Marks: trailing_stop_pending
"""
import numpy as np
import pandas as pd

NAME = "fmz_453246_macd_cross_rsi50_filter_reversal"
FAMILY = "macd_cross"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "fast": [12, 8],
    "slow": [26, 21],
    "rsi_len": [14, 7],
}
DEFAULT_PARAMS = {"fast": 12, "slow": 26, "signal": 9, "rsi_len": 14, "rsi_mid": 50.0}


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


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    c = bars_df["close"]
    macd = c.ewm(span=int(p["fast"]), adjust=False).mean() - c.ewm(span=int(p["slow"]), adjust=False).mean()
    sig = macd.ewm(span=int(p["signal"]), adjust=False).mean()
    r = _rsi(c, int(p["rsi_len"]))
    mid = float(p["rsi_mid"])
    le = (macd > sig) & (macd.shift(1) <= sig.shift(1)) & (r > mid)
    se = (macd < sig) & (macd.shift(1) >= sig.shift(1)) & (r < mid)
    false = pd.Series(False, index=bars_df.index)
    return le, false, se, false.copy()


def portfolio_kwargs(**params):
    return {}
