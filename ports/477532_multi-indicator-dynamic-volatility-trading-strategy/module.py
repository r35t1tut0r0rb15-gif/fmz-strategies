"""Broker days, long only: the SMA 9 crossing over the SMA 21 on volume above 1.5 x its 21-day average with ATR 14 above its 14-day average goes long; the mirror crossing (with the same volume and ATR filters) closes it.
Port of FMZ strategy #477532 "Multi Indicator Dynamic Volatility Trading Strategy" (Advanced Trading Strategy).

FMZ source id: 477532

Source
    https://www.fmz.com/strategy/477532 (PineScript v5, FMZ last modified 2025-01-06 11:47:06).
    Verbatim copy: original_source.md. Read 2026-10-23 (FMZ-C).

Original signal (original_source.md lines 99-150), SMA 9 / 21; volume SMA 21 x 1.5; ATR 14 vs its SMA 14
    buyCondition = crossover(sma9, sma21) and volume > sma(volume, 21) x 1.5 and atr > sma(atr, 14) -> entry Buy
    sellCondition = crossunder(sma9, sma21) and the same filters -> close Buy

Interpretation choices (Pine rules in SURVEY_README.md)
    * The close needs the volume and ATR filters too, so a crossing under on quiet volume leaves the long
      open until a later qualifying crossing (as written). The entry and the close never meet on one bar.
      Long only. No sizing code. Daily bars are broker days (17:00 America/New_York), stamped with their
      first minute. FREQ = "1D" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, SMA crossings filtered by volume and volatility.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: used: the bars' volume column (broker tick volume of the cTrader M1 data, summed per broker day) against 1.5 x its SMA 21; exchange volume to be compared later (Austin, 2026-10-23).
Session open: broker day (17:00 America/New_York, DST by the zone); no venue-open rule.
Long only.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_477532_sma9_21_cross_volume_atr_filter_long_only"
FAMILY = "ma_cross"  # proposed 2026-10-23 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "fast": [9, 12],
    "slow": [21, 30],
}
DEFAULT_PARAMS = {"fast": 9, "slow": 21, "vol_mult": 1.5, "atr_len": 14}


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
    nf, ns, na_ = int(p["fast"]), int(p["slow"]), int(p["atr_len"])
    f, s = c.rolling(nf).mean(), c.rolling(ns).mean()
    pc = c.shift(1)
    atr = _rma(pd.concat([h - lo, (h - pc).abs(), (lo - pc).abs()], axis=1).max(axis=1), na_)
    ok = (v > v.rolling(ns).mean() * float(p["vol_mult"])) & (atr > atr.rolling(na_).mean())
    buy = (f > s) & (f.shift(1) <= s.shift(1)) & ok
    sell = (f < s) & (f.shift(1) >= s.shift(1)) & ok
    ix = bars_df.index
    false = pd.Series(False, index=ix)
    return buy.astype(bool), sell.astype(bool), false, false.copy()


def portfolio_kwargs(**params):
    return {}
