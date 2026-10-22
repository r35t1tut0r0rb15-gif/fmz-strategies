"""Bollinger band re-entries with RSI extremes, broker days: the close crossing back over the lower band (20, 2) with the RSI 14 under 30 goes long, crossing back under the upper band with the RSI over
70 short; reversing.
Port of FMZ strategy #440982 "Bollinger-Bands与RSI组合交易策略Bollinger-Bands-and-RSI-Combination-Trading-Strategy" (Estrategia de Bandas de Bollinger y RSI).

FMZ source id: 440982

Source
    https://www.fmz.com/strategy/440982 (PineScript v4, FMZ last modified 2024-02-04 15:09:35).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 129-161), BB 20 / 2 on close; RSI 14 (70 / 30)
    buy = crossover(close, lower) and rsi < 30 -> entry Buy;  sell = crossunder(close, upper) and rsi > 70 -> entry Sell

Interpretation choices (Pine rules in SURVEY_README.md)
    * Pine's stdev is the population deviation. strategy.entry reverses: REVERSAL INTENDED. No sizing
      code. Daily bars are broker days (17:00 America/New_York), stamped with their first minute. FREQ =
      "1D" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, Bollinger re-entries and RSI.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: DG440982 (2 members, best partner #441136, Jaccard 0.898); ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: broker day (17:00 America/New_York, DST by the zone); no venue-open rule.
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_440982_bb_reentry_rsi_extreme_reversal"
FAMILY = "bollinger_reversion"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "length": [20, 50],
    "rsi_oversold": [30, 40],
}
DEFAULT_PARAMS = {"length": 20, "rsi_oversold": 30, "mult": 2.0, "rsi_length": 14}


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
    n = int(p["length"])
    basis = c.rolling(n).mean()
    dev = float(p["mult"]) * c.rolling(n).std(ddof=0)
    up, lo = basis + dev, basis - dev
    r = _rsi(c, int(p["rsi_length"]))
    os_ = float(p["rsi_oversold"])
    buy = (c > lo) & (c.shift(1) <= lo.shift(1)) & (r < os_)
    sell = (c < up) & (c.shift(1) >= up.shift(1)) & (r > 100 - os_)
    false = pd.Series(False, index=c.index)
    return buy, false, sell & ~buy, false.copy()


def portfolio_kwargs(**params):
    return {}
