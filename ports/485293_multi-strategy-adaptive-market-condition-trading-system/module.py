"""SMA 10 / 50 crosses or Bollinger extremes with RSI, always in, broker days: an SMA 10 cross above SMA 50, or a close
under the lower Bollinger band with RSI 14 below 30, goes long; the opposite cross, or a close over the upper band with
RSI above 70, goes short; each entry reverses the other.
Port of FMZ strategy #485293 "多策略自适应市场条件交易系统-Multi-Strategy-Adaptive-Market-Condition-Trading-System" (Adaptive Trading Strategy).

FMZ source id: 485293

Source
    https://www.fmz.com/strategy/485293 (PineScript v5, FMZ last modified 2025-03-07 09:59:47).
    Verbatim copy: original_source.md. Read 2026-10-17 (FMZ-C laptop lane).

Original signal (original_source.md lines 160-190), SMA 10 / 50, RSI 14 (30 / 70), BB 20 x 2
    buy = (sma10 > sma50 and crossover(sma10, sma50)) or (close < lower and rsi < 30) -> entry long
    sell = (sma10 < sma50 and crossunder(sma10, sma50)) or (close > upper and rsi > 70) -> close long, entry short

Interpretation choices (Pine rules in SURVEY_README.md)
    * Both on one bar (a bullish cross with an overbought upper-band close): the short, written last, wins.
    * Entries reverse (REVERSAL INTENDED). The "strong buy" pattern only draws a label.
    * Daily bars are broker days (17:00 America/New_York), stamped with their first minute; FREQ = "1D" from the
      backtest header. No stops.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, moving averages, bands and an oscillator.
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

NAME = "fmz_485293_sma_cross_or_bb_rsi_extreme"
FAMILY = "multi_indicator_confluence"  # proposed 2026-10-17 (FMZ-C laptop lane), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "slow": [50, 100],
    "bb_mult": [2.0, 2.5],
}
DEFAULT_PARAMS = {"fast": 10, "slow": 50, "rsi_len": 14, "bb_len": 20, "bb_mult": 2.0}


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
    f, s = c.rolling(int(p["fast"])).mean(), c.rolling(int(p["slow"])).mean()
    rsi = _rsi(c, int(p["rsi_len"]))
    n = int(p["bb_len"])
    basis = c.rolling(n).mean()
    dev = p["bb_mult"] * c.rolling(n).std(ddof=0)
    x_up = (f > s) & (f.shift(1) <= s.shift(1))
    x_dn = (f < s) & (f.shift(1) >= s.shift(1))
    buy = x_up | ((c < basis - dev) & (rsi < 30))
    sell = x_dn | ((c > basis + dev) & (rsi > 70))
    false = pd.Series(False, index=bars_df.index)
    return (buy & ~sell).astype(bool), false, sell.astype(bool), false.copy()


def portfolio_kwargs(**params):
    return {}
