"""Broker days: more than half of the last 50 closes above the EMA 20 with the close above it, volume above its 50-day average and ATR 14 over 1 % of the close goes long; the mirror below the EMA goes short; the opposite signal reverses.
Port of FMZ strategy #484581 "多维度EMA趋势追踪与成交量波动率确认策略-Multi-Dimensional-EMA-Trend-Following-with-Volume-and-Volatility-Confirmation-Strategy" (EMA, Hacim ve Volatilite Stratejisi).

FMZ source id: 484581

Source
    https://www.fmz.com/strategy/484581 (PineScript v5, FMZ last modified 2025-03-03 09:59:19).
    Verbatim copy: original_source.md. Read 2026-10-23 (FMZ-C).

Original signal (original_source.md lines 140-192), EMA 20; 50-bar share above / below; volume SMA 50 x 1.0; ATR 14 / close > 1 %
    ratioAbove = share of bars 0 .. 49 with close > ema;  longCondition = ratioAbove > 0.5 and close > ema and volume > sma(volume, 50) and atr / close > 0.01 -> entry Long
    shortCondition = ratioBelow > 0.5 and close < ema and the same filters -> entry Short

Interpretation choices (Pine rules in SURVEY_README.md)
    * Entries only, as states; an opposite entry reverses. The share counts bars where the close and the
      EMA are known (missing history counts as not above / below). REVERSAL INTENDED. Capital is sizing.
      Daily bars are broker days (17:00 America/New_York), stamped with their first minute. FREQ = "1D"
      from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, EMA trend persistence with volume and volatility filters.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: capital stored, not ported.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: used: the bars' volume column (broker tick volume of the cTrader M1 data, summed per broker day) against its SMA 50; exchange volume to be compared later (Austin, 2026-10-23).
Session open: broker day (17:00 America/New_York, DST by the zone); no venue-open rule.
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_484581_ema20_persistence_volume_atr_pct_state_reversal"
FAMILY = "trend_persistence"  # proposed 2026-10-23 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "lookback": [50, 100],
    "atr_pct": [0.01, 0.02],
}
DEFAULT_PARAMS = {"ema_len": 20, "lookback": 50, "atr_pct": 0.01}


def broker_day(index):
    """Broker day of each timestamp: the session ending 17:00 America/New_York, labelled by its
    end date (as worker A's ports). The desktop binds this name to registry_schema.broker_day."""
    ny = index.tz_convert("America/New_York")
    return (ny + pd.Timedelta(hours=7)).normalize().tz_localize(None)


def precompute(raw_1m_df, symbol_key, **params):
    df = raw_1m_df[["open", "high", "low", "close", "volume"]].dropna(subset=["close"])
    if df.index.tz is None:
        raise ValueError("raw_1m_df must have a tz-aware UTC index")
    lab = broker_day(df.index)
    bars = df.groupby(lab).agg({"open": "first", "high": "max", "low": "min", "close": "last", "volume": "sum"})
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
    h, lo, c, v = bars_df["high"], bars_df["low"], bars_df["close"], bars_df["volume"]
    e = c.ewm(span=int(p["ema_len"]), adjust=False).mean()
    n = int(p["lookback"])
    above = (c > e).astype(float).rolling(n, min_periods=1).sum() / n
    below = (c < e).astype(float).rolling(n, min_periods=1).sum() / n
    pc = c.shift(1)
    atr = _rma(pd.concat([h - lo, (h - pc).abs(), (lo - pc).abs()], axis=1).max(axis=1), 14)
    filt = (v > v.rolling(n).mean()) & (atr / c > float(p["atr_pct"]))
    buy = (above > 0.5) & (c > e) & filt
    sell = (below > 0.5) & (c < e) & filt
    ix = bars_df.index
    false = pd.Series(False, index=ix)
    return buy.astype(bool), false, sell.astype(bool), false.copy()


def portfolio_kwargs(**params):
    return {}
