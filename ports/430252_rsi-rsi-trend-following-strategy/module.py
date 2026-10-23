"""The %B of RSI 14 inside its own Bollinger Bands (SMA 50 +/- 1.618 sd), broker days: %B rising back to 0 or above from below goes long, falling back to 1 or below from above goes short; reversing.
Port of FMZ strategy #430252 "基于RSI指标的趋势跟随策略RSI-Trend-Following-Strategy" (Gidra's RSI or MFI Strategy v0.1).

FMZ source id: 430252

Source
    https://www.fmz.com/strategy/430252 (PineScript v2, FMZ last modified 2023-10-26 15:44:15).
    Verbatim copy: original_source.md. Read 2026-10-23 (FMZ-C).

Original signal (original_source.md lines 138-193), RSI 14 (the MFI switch off); BB 50, 1.618; lot 100 %; window 2018 .. 2100
    bbr = (rsi - lower) / (upper - lower) of BB(rsi, 50, 1.618);  bbr >= 0 and bbr[1] < 0 -> entry Long;  bbr <= 1 and bbr[1] > 1 -> entry Short

Interpretation choices (Pine rules in SURVEY_README.md)
    * useRSI is on, so the MFI branch (the only use of volume) never feeds the signal: ported as not using
      volume (check 8). stdev is Pine's population stdev. The author's 2018 .. 2100 window is dropped.
      REVERSAL INTENDED. The equity lot is sizing. Daily bars are broker days (17:00 America/New_York),
      stamped with their first minute. FREQ = "1D" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, RSI %B band re-entries.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: lot = equity / close x 100 % stored, not ported.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: broker day (17:00 America/New_York, DST by the zone); the author's window dropped.
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_430252_rsi14_percent_b_band_reentry_reversal"
FAMILY = "rsi_threshold"  # proposed 2026-10-23 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "length": [50, 20],
    "mult": [1.618, 2.0],
}
DEFAULT_PARAMS = {"length": 50, "mult": 1.618, "rsi_len": 14}


def broker_day(index):
    """Broker day of each timestamp: the session ending 17:00 America/New_York, labelled by its
    end date (as worker A's ports). The desktop binds this name to registry_schema.broker_day."""
    ny = index.tz_convert("America/New_York")
    return (ny + pd.Timedelta(hours=7)).normalize().tz_localize(None)


def precompute(raw_1m_df, symbol_key, **params):
    df = raw_1m_df[["open", "high", "low", "close"]].dropna(subset=["close"])
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
    c = bars_df["close"]
    d = c.diff()
    n = int(p["rsi_len"])
    r = 100 - 100 / (1 + _rma(d.clip(lower=0), n) / _rma((-d).clip(lower=0), n))
    L = int(p["length"])
    basis, dev = r.rolling(L).mean(), float(p["mult"]) * r.rolling(L).std(ddof=0)
    bbr = (r - (basis - dev)) / (2 * dev).replace(0.0, np.nan)
    le = (bbr >= 0) & (bbr.shift(1) < 0)
    se = (bbr <= 1) & (bbr.shift(1) > 1)
    false = pd.Series(False, index=c.index)
    return le, false, se & ~le, false.copy()


def portfolio_kwargs(**params):
    return {}
