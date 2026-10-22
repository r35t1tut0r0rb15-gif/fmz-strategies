"""RSI 14 extremes outside the Bollinger 30 / 2 bands against the SMA 20 / 50 order, broker days: RSI under 25 below the lower band with the SMA 20 above the SMA 50 goes long, RSI over 80 above the upper band with the SMA 20 below goes short; reversing.
Port of FMZ strategy #477613 "Multi Technical Indicator Fusion Trend Following Quantitative Trading Strategy" (RSI + MA + BB30 Strategy).

FMZ source id: 477613

Source
    https://www.fmz.com/strategy/477613 (PineScript v5, FMZ last modified 2025-01-06 16:57:57).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 88-145), RSI 14, 80 / 25; SMA 20 / 50; BB 30 / 2
    rsi < 25 and sma20 > sma50 and close < lower -> entry Long;  rsi > 80 and sma20 < sma50 and close > upper -> entry Short

Interpretation choices (Pine rules in SURVEY_README.md)
    * There is no exit: positions end at the opposite entry. REVERSAL INTENDED. No sizing code. Daily
      bars are broker days (17:00 America/New_York), stamped with their first minute. FREQ = "1D" from
      the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, RSI / band extremes against the SMA order.
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

NAME = "fmz_477613_rsi14_bb30_extreme_sma20_50_pullback_reversal"
FAMILY = "bollinger_reversion"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "rsi_low": [25, 30],
    "bb_length": [30, 20],
}
DEFAULT_PARAMS = {"rsi_low": 25, "bb_length": 30, "rsi_high": 80, "rsi_length": 14}


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
    r = _rsi(c, int(p["rsi_length"]))
    m20, m50 = c.rolling(20).mean(), c.rolling(50).mean()
    n = int(p["bb_length"])
    basis = c.rolling(n).mean()
    dev = 2 * c.rolling(n).std(ddof=0)
    le = (r < float(p["rsi_low"])) & (m20 > m50) & (c < basis - dev)
    se = (r > float(p["rsi_high"])) & (m20 < m50) & (c > basis + dev)
    false = pd.Series(False, index=c.index)
    return le, false, se, false.copy()


def portfolio_kwargs(**params):
    return {}
