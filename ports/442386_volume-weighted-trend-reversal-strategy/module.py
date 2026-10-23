"""Broker days: the close above a 14-bar volume-weighted average and above the "QQE mod" line (the EMA 14 +- 5 deviations of the close from it, upper when a smoothed RSI 14 is above 50) goes long; the close below both goes short; reversing.
Port of FMZ strategy #442386 "Volume Weighted Trend Reversal Strategy" (VWAP and QQE Mod Strategy).

FMZ source id: 442386

Source
    https://www.fmz.com/strategy/442386 (PineScript v5, FMZ last modified 2024-02-21 15:04:34).
    Verbatim copy: original_source.md. Read 2026-10-23 (FMZ-C).

Original signal (original_source.md lines 167-201), QQE length 14, smoothing 5, filter 5; VWAP = sma(close x volume, 14) / sma(volume, 14)
    j := (1 - 1 / 5) x nz(j[1]) + 1 / 5 x (rsi(close, 14) - 50);  qqeModValue = j > 0 ? ema14 + 5 x stdev(close - ema14, 14) : ema14 - 5 x stdev
    buySignal = close > vwap and close > qqeModValue -> entry Buy;  sellSignal = close < vwap and close < qqeModValue -> entry Sell

Interpretation choices (Pine rules in SURVEY_README.md)
    * j starts from 0 once the RSI exists. With j > 0 the line is the upper band 5 deviations above the
      EMA, so longs need a close above it (rare); with j <= 0 it is the lower band (weird case). Entries
      repeat while their conditions hold. Pine's stdev is the population deviation. REVERSAL INTENDED. No
      sizing code. Daily bars are broker days (17:00 America/New_York), stamped with their first minute.
      FREQ = "1D" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, close against a volume-weighted average and an RSI-switched band.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: used: the bars' volume column (broker tick volume of the cTrader M1 data, summed per bar) as the weights of the 14-bar VWAP; exchange volume to be compared later (Austin, 2026-10-23).
Session open: broker day (17:00 America/New_York, DST by the zone); no venue-open rule.
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_442386_vwap14_qqe_mod_band_reversal"
FAMILY = "qqe"  # proposed 2026-10-23 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "length": [14, 28],
    "filter_len": [5, 2],
}
DEFAULT_PARAMS = {"length": 14, "m": 5, "filter_len": 5}


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


def _rsi(x, n):
    d = x.diff()
    up, dn = _rma(d.clip(lower=0), n), _rma((-d).clip(lower=0), n)
    out = 100 - 100 / (1 + up / dn.where(dn != 0))
    return out.where(up != 0, 0.0).where(dn != 0, 100.0).where(up.notna() & dn.notna())


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    c, v = bars_df["close"], bars_df["volume"]
    n = int(p["length"])
    sv = v.rolling(n).mean()
    vwap = (c * v).rolling(n).mean() / sv.where(sv != 0)
    ema = c.ewm(span=n, adjust=False).mean()
    rsi = _rsi(c, n).to_numpy()
    mm = float(p["m"])
    jv = np.full(len(rsi), np.nan)
    prev = np.nan
    for i in range(len(rsi)):
        base = 0.0 if np.isnan(prev) else prev
        jv[i] = (1.0 - 1.0 / mm) * base + 1.0 / mm * (rsi[i] - 50)
        prev = jv[i]
    sd = (c - ema).rolling(n).std(ddof=0)
    fl = float(p["filter_len"])
    line = pd.Series(np.where(jv > 0, ema + fl * sd, ema - fl * sd), index=c.index)
    buy = (c > vwap) & (c > line)
    sell = (c < vwap) & (c < line)
    ix = bars_df.index
    false = pd.Series(False, index=ix)
    return buy.astype(bool), false, sell.astype(bool), false.copy()


def portfolio_kwargs(**params):
    return {}
