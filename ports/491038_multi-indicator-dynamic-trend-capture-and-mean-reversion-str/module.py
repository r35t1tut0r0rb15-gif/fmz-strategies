"""EMA 9 / 21 trend with an SMA 20 / Bollinger-basis side and an RSI cap, always in, broker days: EMA 9 above EMA 21,
the close above SMA 20 and the basis and RSI 14 below 60 is long; the mirror (RSI above 40) is short; each side's
condition also closes the other.
Port of FMZ strategy #491038 "多指标动态趋势捕捉与均值回归策略-Multi-Indicator-Dynamic-Trend-Capture-and-Mean-Reversion-Strategy" (Phoenix Pro Strategy).

FMZ source id: 491038

Source
    https://www.fmz.com/strategy/491038 (PineScript v5, FMZ last modified 2025-04-18 09:27:27).
    Verbatim copy: original_source.md. Read 2026-10-17 (FMZ-C laptop lane).

Original signal (original_source.md lines 184-239), EMA 9 / 21, SMA 20, RSI 14, Bollinger basis SMA 20
    long = ema9 > ema21 and close > sma20 and rsi < 60 and close > basis
    short = ema9 < ema21 and close < sma20 and rsi > 40 and close < basis
    entry long when long, close "Long" when short; entry short when short, close "Short" when long

Interpretation choices (Pine rules in SURVEY_README.md)
    * Pivots, the SMA 50, the Bollinger bands and the zigzag are drawn only (the zigzag tests high >= high x 1.05,
      never true); not used.
    * Every condition bar is an entry (a same-side entry while held is ignored); the closes fall on the opposite
      entries' bars, so the strategy reverses (REVERSAL INTENDED). The two conditions cannot hold on one bar.
    * Daily bars are broker days (17:00 America/New_York), stamped with their first minute; FREQ = "1D" from the
      backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, moving averages and an oscillator.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: broker day (17:00 America/New_York, DST by the zone); no venue-open rule.
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_491038_phoenix_ema_sma_rsi_always_in"
FAMILY = "ma_trend"  # proposed 2026-10-17 (FMZ-C laptop lane), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "ema_fast": [9, 5],
    "sma_short": [20, 50],
}
DEFAULT_PARAMS = {"ema_fast": 9, "ema_slow": 21, "sma_short": 20, "rsi_len": 14, "rsi_cap_long": 60,
                  "rsi_floor_short": 40, "bb_length": 20}


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
    r = 100 - 100 / (1 + up / dn)
    r = r.where(up != 0, 0.0)
    return r.where(dn != 0, 100.0).where(up.notna() & dn.notna())


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    c = bars_df["close"]
    ef = c.ewm(span=int(p["ema_fast"]), adjust=False).mean()
    es = c.ewm(span=int(p["ema_slow"]), adjust=False).mean()
    sma = c.rolling(int(p["sma_short"])).mean()
    basis = c.rolling(int(p["bb_length"])).mean()
    rsi = _rsi(c, int(p["rsi_len"]))
    long_c = ((ef > es) & (c > sma) & (rsi < p["rsi_cap_long"]) & (c > basis)).astype(bool)
    short_c = ((ef < es) & (c < sma) & (rsi > p["rsi_floor_short"]) & (c < basis)).astype(bool)
    false = pd.Series(False, index=bars_df.index)
    return long_c, false, short_c, false.copy()


def portfolio_kwargs(**params):
    return {}
