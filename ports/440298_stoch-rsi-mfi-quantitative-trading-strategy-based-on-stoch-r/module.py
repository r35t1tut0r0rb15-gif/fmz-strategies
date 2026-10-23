"""Broker days: a stochastic of RSI 11 (highest 11 / lowest 7, SMA 3) crossing over 20, or an MFI 14 computed on the volume series crossing over 20, goes long; the stochastic crossing under 70 or that MFI crossing under 70 goes short; reversing.
Port of FMZ strategy #440298 "基于Stoch-RSI和MFI的量化交易策略Quantitative-Trading-Strategy-Based-on-Stoch-RSI-and-MFI" (MFI and Stoch RSI Bot (carterac)).

FMZ source id: 440298

Source
    https://www.fmz.com/strategy/440298 (PineScript v5, FMZ last modified 2024-01-29 10:11:14).
    Verbatim copy: original_source.md. Read 2026-10-23 (FMZ-C).

Original signal (original_source.md lines 147-185), RSI 11 (inputs 14 / 3 / 3 unused); stochastic window highest 11, lowest 7, SMA 3; MFI 14 of volume; 20 / 70
    k = sma(100 * (rsi(close, 11) - lowest(rsi, 7)) / (highest(rsi, 11) - lowest(rsi, 7)), 3);  mfiValue = mfi(volume, 14)
    crossover(k, 20) or crossover(mfi, 20) -> entry Buy;  crossunder(k, 70) or crossunder(mfi, 70) -> entry Sell

Interpretation choices (Pine rules in SURVEY_README.md)
    * The stochastic uses a fixed RSI 11 with different high / low windows, not the length inputs
      (weird case). ta.mfi(volume, 14) takes volume as its source, so it measures volume moves weighted by
      volume (weird case). When both sides signal on one bar the later call (short) wins. REVERSAL
      INTENDED. No sizing code. Daily bars are broker days (17:00 America/New_York), stamped with their
      first minute. FREQ = "1D" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, stochastic-RSI and volume-MFI threshold crossings.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: used: the bars' volume column (broker tick volume of the cTrader M1 data, summed per bar) as both the source and the weight of the MFI 14; exchange volume to be compared later (Austin, 2026-10-23).
Session open: broker day (17:00 America/New_York, DST by the zone); no venue-open rule.
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_440298_stoch_rsi11_and_volume_mfi_cross_reversal"
FAMILY = "stochastic_rsi"  # proposed 2026-10-23 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "oversold": [20.0, 30.0],
    "overbought": [70.0, 80.0],
}
DEFAULT_PARAMS = {"rsi_len": 11, "hi_len": 11, "lo_len": 7, "smooth": 3, "mfi_len": 14, "oversold": 20.0,
                  "overbought": 70.0}


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


def _mfi(src, vol, n):
    """Pine ta.mfi: money-flow ratio over n bars; 100 when the falling flow is 0, 0 when the rising is 0."""
    ch = src.diff()
    upper = (vol * src.where(~(ch <= 0), 0.0)).rolling(n).sum()
    lower = (vol * src.where(~(ch >= 0), 0.0)).rolling(n).sum()
    out = 100.0 - 100.0 / (1.0 + upper / lower.where(lower != 0))
    return out.where(upper != 0, 0.0).where(lower != 0, 100.0).where(upper.notna() & lower.notna())


def _over(a, x):
    return (a > x) & (a.shift(1) <= x)


def _under(a, x):
    return (a < x) & (a.shift(1) >= x)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    c, v = bars_df["close"], bars_df["volume"]
    r = _rsi(c, int(p["rsi_len"]))
    hi, lo = r.rolling(int(p["hi_len"])).max(), r.rolling(int(p["lo_len"])).min()
    rng = hi - lo
    k = (100 * (r - lo) / rng.where(rng != 0)).rolling(int(p["smooth"])).mean()
    mf = _mfi(v, v, int(p["mfi_len"]))
    os_, ob = float(p["oversold"]), float(p["overbought"])
    buy = _over(k, os_) | _over(mf, os_)
    sell = _under(k, ob) | _under(mf, ob)
    ix = bars_df.index
    false = pd.Series(False, index=ix)
    return (buy & ~sell).astype(bool), false, sell.astype(bool), false.copy()


def portfolio_kwargs(**params):
    return {}
