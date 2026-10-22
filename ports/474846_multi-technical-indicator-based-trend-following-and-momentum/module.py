"""EMA 200 trend with MACD and RSI states, daily bars, long only: while the close is over the EMA 200, MACD over its signal and RSI 14 between 50 and 70 it buys; MACD under its signal, the close under the EMA 200 or RSI over 70 sells.
Port of FMZ strategy #474846 "Multi Technical Indicator Based Trend Following and Momentum Strategy" (Simplified SOL/USDT Strategy).

FMZ source id: 474846

Source
    https://www.fmz.com/strategy/474846 (PineScript v5, FMZ last modified 2024-12-12 15:01:09).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 116-155), MACD 12 / 26 / 9; EMA 200; RSI 14; 100 % of equity
    close > ema200 and macd > signal and 50 < rsi < 70 -> entry Long;  macd < signal or close < ema200 or rsi > 70 -> close Long

Interpretation choices (Pine rules in SURVEY_README.md)
    * The entry and close tests cannot hold on one bar; entries repeat while held (ignored). Long only.
      The equity share is not ported. FREQ = "1D" from the backtest header (broker days).

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, trend / momentum states.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: percent-of-equity size stored, not ported.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
Long only.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_474846_ema200_macd_rsi50_70_state_long"
FAMILY = "multi_indicator_confluence"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "ema_length": [200, 100],
    "rsi_length": [14, 7],
}
DEFAULT_PARAMS = {"ema_length": 200, "rsi_length": 14}


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
    macd = c.ewm(span=12, adjust=False).mean() - c.ewm(span=26, adjust=False).mean()
    sig = macd.ewm(span=9, adjust=False).mean()
    e = c.ewm(span=int(p["ema_length"]), adjust=False).mean()
    r = _rsi(c, int(p["rsi_length"]))
    le = (c > e) & (macd > sig) & (r > 50) & (r < 70)
    lx = (macd < sig) | (c < e) | (r > 70)
    false = pd.Series(False, index=bars_df.index)
    return le, lx, false, false.copy()


def portfolio_kwargs(**params):
    return {}
