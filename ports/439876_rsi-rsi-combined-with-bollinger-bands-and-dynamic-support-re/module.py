"""RSI 14 crossings out of the extremes, broker days: the RSI crossing back over 30 goes long, crossing back under 70 goes short; reversing (the support / resistance and band tests filter nothing).
Port of FMZ strategy #439876 "RSI与布林带支撑阻力动态结合量化策略RSI-Combined-with-Bollinger-Bands-and-Dynamic-Support-Resistance-Quantitative-Strategy" (RSI + BB + S/R Strategy with Trend Filter).

FMZ source id: 439876

Source
    https://www.fmz.com/strategy/439876 (PineScript v5, FMZ last modified 2024-01-24 15:19:22).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 140-262), RSI 14, 70 / 30; BB 20 x 2 (plot only); pivot S/R 10, 20 pivots, 10 % width, 5 levels, strength 2; trend filter off
    buy = crossover(rsi, 30) and close <= highest(high, 5) and close >= lowest(low, 5) and (not trend filter);  sell = crossunder(rsi, 70) and the same range test;  entry Buy / entry Sell

Interpretation choices (Pine rules in SURVEY_README.md)
    * The S/R arrays are built but no order reads them; the "proximity" test compares the close with
      the 5-bar high and low that include the current bar, so it always holds. The trend filter is off.
      strategy.entry reverses: REVERSAL INTENDED. No sizing code. Daily bars are broker days (17:00
      America/New_York), stamped with their first minute. FREQ = "1D" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, RSI crossings.
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

NAME = "fmz_439876_rsi14_extreme_exit_crossings"
FAMILY = "rsi_oscillator"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "rsi_length": [14, 7],
    "oversold": [30, 20],
}
DEFAULT_PARAMS = {"rsi_length": 14, "oversold": 30}


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
    up = _rma(d.clip(lower=0), n)
    dn = _rma((-d).clip(lower=0), n)
    with np.errstate(divide="ignore", invalid="ignore"):
        r = 100.0 - 100.0 / (1.0 + up / dn)
    r = r.where(up != 0, 0.0).where(dn != 0, 100.0)    # Pine: down == 0 -> 100, else up == 0 -> 0
    return r.where(up.notna() & dn.notna())


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    c = bars_df["close"]
    r = _rsi(c, int(p["rsi_length"]))
    os_ = float(p["oversold"])
    ob = 100 - os_
    up = (r > os_) & (r.shift(1) <= os_)
    dn = (r < ob) & (r.shift(1) >= ob)
    false = pd.Series(False, index=c.index)
    return up, false, dn, false.copy()


def portfolio_kwargs(**params):
    return {}
