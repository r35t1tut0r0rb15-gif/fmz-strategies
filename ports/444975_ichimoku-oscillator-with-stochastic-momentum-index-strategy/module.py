"""Stochastic Momentum Index against its signal with an Ichimoku-style oscillator's sign, daily bars: SMI above its signal with the oscillator above zero goes long, SMI below with it below zero goes short;
reversing.
Port of FMZ strategy #444975 "Ichimoku Oscillator with Stochastic Momentum Index Strategy" (Ichimoku Oscillator with SMI (IOSMI)).

FMZ source id: 444975

Source
    https://www.fmz.com/strategy/444975 (PineScript v5, FMZ last modified 2024-03-15 16:23:55).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 157-189), SMI %K 21, %D 9; oscillator ema(hl2, 9) / 2 + ema(hl2, 26) / 2 + sma(close, 14) - ema(hl2, 52) - sma(open, 14)
    SMI = ema(ema(close - mid(21), 9), 9) / (ema(ema(range(21), 9), 9) / 2) x 100;  signal = ema(SMI, 9)
    SMI > signal and io > 0 -> entry Buy;  SMI < signal and io < 0 -> entry Sell

Interpretation choices (Pine rules in SURVEY_README.md)
    * Both conditions are levels, so a repeated entry while already on that side is ignored (one
      position). The SMI is 0 while the smoothed range is 0 or still undefined (the test on na is
      false), so its signal EMA starts from those zeros, as written. strategy.entry reverses:
      REVERSAL INTENDED. No sizing code. FREQ = "1D" from the backtest header (broker days).

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, SMI against its signal with an oscillator filter.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_444975_smi_signal_ichimoku_osc_sign_reversal"
FAMILY = "momentum_oscillator"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "k_len": [21, 10],
    "d_len": [9, 3],
}
DEFAULT_PARAMS = {"k_len": 21, "d_len": 9}


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


def _ema(x, n):
    return x.ewm(span=int(n), adjust=False).mean()


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    o, h, lo, c = (bars_df[k] for k in ("open", "high", "low", "close"))
    hl2 = (h + lo) / 2
    io = _ema(hl2, 9) / 2 + _ema(hl2, 26) / 2 + c.rolling(14).mean() - _ema(hl2, 52) - o.rolling(14).mean()
    a, b = int(p["k_len"]), int(p["d_len"])
    ll, hh = lo.rolling(a).min(), h.rolling(a).max()
    avgrel = _ema(_ema(c - (hh + ll) / 2, b), b)
    avgdiff = _ema(_ema(hh - ll, b), b)
    smi = (avgrel / (avgdiff / 2) * 100).where(avgdiff.notna() & (avgdiff != 0), 0.0)   # na != 0 is false in Pine
    sig = _ema(smi, b)
    le = (smi > sig) & (io > 0)
    se = (smi < sig) & (io < 0)
    false = pd.Series(False, index=bars_df.index)
    return le & ~se, false, se, false.copy()


def portfolio_kwargs(**params):
    return {}
