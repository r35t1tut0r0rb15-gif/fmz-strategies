"""MACD 12 / 26 / 9 crossings beyond the (undisplaced) Ichimoku spans with an RSI filter, daily bars: the cross up with the close over both spans and RSI over 30 goes long, the cross down under both spans with RSI under 70 goes short; any opposite MACD cross closes the position; reversing.
Port of FMZ strategy #474859 "Trend Following Cloud Momentum Divergence Strategy" (Ichimoku + RSI + MACD Strategy).

FMZ source id: 474859

Source
    https://www.fmz.com/strategy/474859 (PineScript v5, FMZ last modified 2024-12-12 15:51:18).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 146-201), Ichimoku 9 / 26 / 52 (spans compared undisplaced); RSI 14, 70 / 30; MACD 12 / 26 / 9 (constants)
    close > spanA and close > spanB and rsi > 30 and crossover(macd, signal) -> entry Long;  mirror -> entry Short;  crossunder(macd, signal) and long -> close Long;  crossover and short -> close Short

Interpretation choices (Pine rules in SURVEY_README.md)
    * The entry tests use the spans of the current bar (the displacement is only in the plots), as
      written. A close coinciding with the opposite entry only repeats the reversal (#437773), so it is
      masked on entry bars. REVERSAL INTENDED. No sizing code. FREQ = "1D" from the backtest header
      (broker days).

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, MACD crossings beyond the spans with an RSI filter.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (1 trial), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_474859_macd_cross_beyond_spans_rsi_reversal"
FAMILY = "ichimoku"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {}
DEFAULT_PARAMS = {}


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


def _mid(h, lo, n):
    return (h.rolling(n).max() + lo.rolling(n).min()) / 2


def simulate(bars_df, **params):
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    ten, kij = _mid(h, lo, 9), _mid(h, lo, 26)
    sa, sb = (ten + kij) / 2, _mid(h, lo, 52)
    r = _rsi(c, 14)
    macd = c.ewm(span=12, adjust=False).mean() - c.ewm(span=26, adjust=False).mean()
    sig = macd.ewm(span=9, adjust=False).mean()
    up = (macd > sig) & (macd.shift(1) <= sig.shift(1))
    dn = (macd < sig) & (macd.shift(1) >= sig.shift(1))
    le = (c > sa) & (c > sb) & (r > 30) & up
    se = (c < sa) & (c < sb) & (r < 70) & dn
    return le, dn & ~se, se, up & ~le


def portfolio_kwargs(**params):
    return {}
