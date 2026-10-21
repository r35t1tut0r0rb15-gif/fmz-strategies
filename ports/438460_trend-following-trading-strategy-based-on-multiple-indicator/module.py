"""MACD, stochastic and EMA agreement where one of them has just crossed, broker days: with the MACD histogram above 0, the stochastic K above D and the close above the EMA 10, a fresh crossing of any one
of the three goes long; the mirror goes short; reversing.
Port of FMZ strategy #438460 "Trend Following Trading Strategy Based on Multiple Indicators" (Rule Number 1 Signals).

FMZ source id: 438460

Source
    https://www.fmz.com/strategy/438460 (PineScript v3, FMZ last modified 2024-01-12 11:25:04).
    Verbatim copy: original_source.md. Read 2026-10-21 (FMZ-C).

Original signal (original_source.md lines 119-159), MACD 8 / 17 / 9; stochastic 14, K 5, D 5 (80 / 20 only colour); EMA 10
    buy = (cross up of the histogram and K > D and close > ema) or (histogram > 0 and K crosses over D and close > ema) or (histogram > 0 and K > D and close crosses over ema) -> entry Rule 1 Buy;  sell mirror -> entry Rule 1 Sell

Interpretation choices (Pine rules in SURVEY_README.md)
    * The overbought / oversold levels only colour the background. strategy.entry reverses: REVERSAL
      INTENDED. No sizing code. Daily bars are broker days (17:00 America/New_York), stamped with their
      first minute. FREQ = "1D" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, MACD, stochastic and EMA crossings.
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

NAME = "fmz_438460_rule1_macd_stoch_ema"
FAMILY = "multi_indicator_confluence"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "stoch_len": [14, 9],
    "ema_signal": [10, 20],
}
DEFAULT_PARAMS = {"stoch_len": 14, "ema_signal": 10, "fast": 8, "slow": 17, "macd_len": 9, "smooth_k": 5,
                  "smooth_d": 5}


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


def _xo(a, b):
    return (a > b) & (a.shift(1) <= b.shift(1))


def _xu(a, b):
    return (a < b) & (a.shift(1) >= b.shift(1))


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    macd = c.ewm(span=int(p["fast"]), adjust=False).mean() - c.ewm(span=int(p["slow"]), adjust=False).mean()
    delta = macd - macd.ewm(span=int(p["macd_len"]), adjust=False).mean()
    n = int(p["stoch_len"])
    ll, hh = lo.rolling(n).min(), h.rolling(n).max()
    with np.errstate(divide="ignore", invalid="ignore"):
        st = 100.0 * (c - ll) / (hh - ll).where(hh > ll)
    k = st.rolling(int(p["smooth_k"])).mean()
    d = k.rolling(int(p["smooth_d"])).mean()
    ema = c.ewm(span=int(p["ema_signal"]), adjust=False).mean()
    zero = pd.Series(0.0, index=c.index)
    buy = ((_xo(delta, zero) & (k > d) & (c > ema)) | ((delta > 0) & _xo(k, d) & (c > ema))
           | ((delta > 0) & (k > d) & _xo(c, ema)))
    sell = ((_xu(delta, zero) & (k < d) & (c < ema)) | ((delta < 0) & _xu(k, d) & (c < ema))
            | ((delta < 0) & (k < d) & _xu(c, ema)))
    false = pd.Series(False, index=c.index)
    return buy, false, sell, false.copy()


def portfolio_kwargs(**params):
    return {}
