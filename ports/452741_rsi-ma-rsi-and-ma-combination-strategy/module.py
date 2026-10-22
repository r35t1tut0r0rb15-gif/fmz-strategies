"""RSI 14 strength in an EMA 12 / 26 uptrend, daily bars, long only: an RSI over 70 with the close over the EMA 12 over the EMA 26 buys; the EMA 26 crossing over the EMA 12 sells.
Port of FMZ strategy #452741 "RSI与MA组合策略RSI-and-MA-Combination-Strategy" (RSI Strategy with Customizable MA and StochRSI Alert).

FMZ source id: 452741

Source
    https://www.fmz.com/strategy/452741 (PineScript v5, FMZ last modified 2024-05-28 17:34:11).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 91-165), RSI 14 over 70; EMA 12 / 26 (MA type EMA); Stoch RSI alerts plotted only
    rsi > 70 and close > ema12 and ema12 > ema26 -> entry Buy;  crossover(ema26, ema12) -> close Buy

Interpretation choices (Pine rules in SURVEY_README.md)
    * With both averages shown (the defaults) the first branch of each test applies. The entry is a
      state (a repeat while long is ignored); the entry and the close cannot meet on one bar. The
      Stoch RSI alerts are only plotted. Long only. No sizing code. FREQ = "1D" from the backtest
      header (broker days).

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, RSI strength in an EMA uptrend.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (8 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
Long only.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_452741_rsi70_strength_ema12_26_uptrend_long"
FAMILY = "rsi_oscillator"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "ob": [70, 60],
    "short_len": [12, 9],
    "long_len": [26, 50],
}
DEFAULT_PARAMS = {"ob": 70.0, "short_len": 12, "long_len": 26, "rsi_len": 14}


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
    return 100 - 100 / (1 + up / dn)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    c = bars_df["close"]
    ms = c.ewm(span=int(p["short_len"]), adjust=False).mean()
    ml = c.ewm(span=int(p["long_len"]), adjust=False).mean()
    r = _rsi(c, int(p["rsi_len"]))
    le = (r > float(p["ob"])) & (c > ms) & (ms > ml)
    lx = (ml > ms) & (ml.shift(1) <= ms.shift(1))
    false = pd.Series(False, index=bars_df.index)
    return le, lx, false, false.copy()


def portfolio_kwargs(**params):
    return {}
