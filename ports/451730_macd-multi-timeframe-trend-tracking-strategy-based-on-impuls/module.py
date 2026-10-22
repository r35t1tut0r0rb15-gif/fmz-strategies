"""LazyBear's Impulse MACD, daily bars, long only: the impulse line (the zero-lag EMA 34 of hlc3 beyond the SMMA 34 channel of highs / lows) crossing over its SMA 9 signal buys; crossing under it sells.
Port of FMZ strategy #451730 "基于脉冲MACD和双均线交叉的多时间尺度趋势追踪策略-Multi-timeframe-Trend-Tracking-Strategy-Based-on-Impulse-MACD-and-Dual-Moving-Average-Crossover" (Impulse MACD Strategy [LazyBear] (IMACD_Strategy)).

FMZ source id: 451730

Source
    https://www.fmz.com/strategy/451730 (PineScript v5, FMZ last modified 2024-05-17 15:33:02).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 92-151), SMMA 34 of high / low; ZLEMA 34 of hlc3; signal SMA 9
    md = mi > hi ? mi - hi : mi < lo ? mi - lo : 0;  sb = sma(md, 9);  crossover(md, sb) -> entry Buy;  crossunder(md, sb) -> close Buy

Interpretation choices (Pine rules in SURVEY_README.md)
    * The SMMA starts from the SMA of its first values, then Wilder's recursion; the ZLEMA is
      2 x EMA - EMA of the EMA. The block under '// Function to calculate SMA' (lines 101-106) is a
      broken leftover that defines nothing the orders use. Long only. No sizing code. FREQ = "1D" from
      the backtest header (broker days).

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, impulse MACD signal crossings.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
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

NAME = "fmz_451730_impulse_macd_signal_cross_long"
FAMILY = "macd_cross"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "length_ma": [34, 20],
    "length_signal": [9, 5],
}
DEFAULT_PARAMS = {"length_ma": 34, "length_signal": 9}


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


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    n = int(p["length_ma"])
    src = (h + lo + c) / 3
    hi, lw = _rma(h, n), _rma(lo, n)
    e1 = src.ewm(span=n, adjust=False).mean()
    e2 = e1.ewm(span=n, adjust=False).mean()
    mi = 2 * e1 - e2
    md = pd.Series(np.where(mi > hi, mi - hi, np.where(mi < lw, mi - lw, 0.0)), index=c.index)  # 0 while na, as Pine
    sb = md.rolling(int(p["length_signal"])).mean()
    le = (md > sb) & (md.shift(1) <= sb.shift(1))
    lx = (md < sb) & (md.shift(1) >= sb.shift(1))
    false = pd.Series(False, index=bars_df.index)
    return le, lx, false, false.copy()


def portfolio_kwargs(**params):
    return {}
