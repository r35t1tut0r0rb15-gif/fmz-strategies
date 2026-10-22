"""ATR-band breakouts of a 2-bar price average, daily bars, long only: the SMA 2 crossing over EMA 11 + 2 ATR(11) goes long, crossing under EMA 11 - 2 ATR closes.
Port of FMZ strategy #451027 "RSI50_EMA长仓策略-RSI50_EMA-Long-Only-Strategy" (RSI50_EMA Long Only Strategy).

FMZ source id: 451027

Source
    https://www.fmz.com/strategy/451027 (PineScript v4, FMZ last modified 2024-05-11 11:49:29).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 91-122), EMA 11; ATR 11 x 2; price = SMA 2; RSI 20 cap 50 (second id); 100 % of equity
    crossover(sma2, ema11 + 2 atr) -> entry Buy;  crossover(ema11 - 2 atr, sma2) -> close Buy;  crossover(rsi20, 50) -> entry RSI (when the same breakout);  crossunder(rsi20, 50) -> close RSICLose (never entered)

Interpretation choices (Pine rules in SURVEY_README.md)
    * The RSI block only adds a second long id on a bar that already sends the Buy entry, which the
      default pyramiding refuses, and its close names an id that is never entered, so it never acts.
      Long only. The 100 % of equity size is sizing. FREQ = "1D" from the backtest header (broker
      days).

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, ATR-band breakouts of a smoothed price.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: the 100 % of equity size stored.
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

NAME = "fmz_451027_sma2_atr_band_breakout_long"
FAMILY = "volatility_channel_breakout"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "length": [11, 20],
    "mult": [2.0, 1.0],
}
DEFAULT_PARAMS = {"length": 11, "mult": 2.0}


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
    n = int(p["length"])
    price = c.rolling(2).mean()
    avg = c.ewm(span=n, adjust=False).mean()
    pc = c.shift(1)
    tr = pd.concat([h - lo, (h - pc).abs(), (lo - pc).abs()], axis=1).max(axis=1)
    diff = _rma(tr, n) * float(p["mult"])
    bull, bear = avg + diff, avg - diff
    le = (price > bull) & (price.shift(1) <= bull.shift(1))
    lx = (bear > price) & (bear.shift(1) <= price.shift(1))
    false = pd.Series(False, index=bars_df.index)
    return le, lx, false, false.copy()


def portfolio_kwargs(**params):
    return {}
