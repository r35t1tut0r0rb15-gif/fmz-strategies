"""A MACD (EMA 12 / 26, signal 9) of an altered on-balance volume (volume added on up closes and on down closes with a white candle, subtracted otherwise): a rising MACD crossing over its signal goes long; a falling MACD under its signal, with the price MACD 12 / 26 / 9 under its signal and two lower lows, goes short; broker days, reversing.
Port of FMZ strategy #432241 "基于改动OBV和MACD的量化交易策略Altered-OBV-and-MACD-Quantitative-Trading-Strategy" (Altered OBV On MACD (stocktechbot)).

FMZ source id: 432241

Source
    https://www.fmz.com/strategy/432241 (PineScript v5, FMZ last modified 2023-11-15 17:58:42).
    Verbatim copy: original_source.md. Read 2026-10-23 (FMZ-C).

Original signal (original_source.md lines 169-245), MACD 12 / 26, signal 9, EMA / EMA; price MACD 12 / 26 / 9; SMAs 200 / 50 / 90 / 21 / 9 (plots and unused conditions)
    chng = close < close[1] and open < close ? 1 : close > close[1] ? 1 : -1;  obvalt = cum(sign(chng) x volume);  macd = ema(obvalt, 12) - ema(obvalt, 26);  signal = ema(macd, 9)
    crossover(macd, signal) and rising(macd, 2) -> entry long;  falling(macd, 1) and macd < signal and macdLine < signalLine and falling(low, 2) -> entry short

Interpretation choices (Pine rules in SURVEY_README.md)
    * ta.rising(x, 2) is read as above both of the previous two values, ta.falling(x, 1) as under the
      previous value, as earlier ports. On the first bar close[1] is na, so chng = -1. The cumulative
      OBV's start does not move the MACD (an EMA difference drops a constant). The SMA conditions
      (mafentry, matwohun, ...) are computed but no order uses them. The two entry conditions cannot hold
      on one bar. REVERSAL INTENDED. margin_long / margin_short 100 are sizing. Daily bars are broker days
      (17:00 America/New_York), stamped with their first minute. FREQ = "1D" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, MACD of an on-balance volume variant.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: strategy(): margin_long 100, margin_short 100, not ported.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: used: the bars' volume column (broker tick volume of the cTrader M1 data, summed per bar) in the altered OBV (cumulative signed volume) whose MACD gives both entries; exchange volume to be compared later (Austin, 2026-10-23).
Session open: broker day (17:00 America/New_York, DST by the zone); no venue-open rule.
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_432241_altered_obv_macd_cross_price_macd_filter_reversal"
FAMILY = "obv"  # proposed 2026-10-23 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "fast_len": [12, 8],
    "slow_len": [26, 34],
}
DEFAULT_PARAMS = {"fast_len": 12, "slow_len": 26, "signal_len": 9}


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


def _ema(x, n):
    return x.ewm(span=n, adjust=False).mean()


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    o, lo, c, v = (bars_df[k] for k in ("open", "low", "close", "volume"))
    pc = c.shift(1)
    chng = np.where((c < pc) & (o < c), 1.0, np.where(c > pc, 1.0, -1.0))
    obv = (pd.Series(chng, index=c.index) * v).cumsum()
    macd = _ema(obv, int(p["fast_len"])) - _ema(obv, int(p["slow_len"]))
    sig = _ema(macd, int(p["signal_len"]))
    pm = _ema(c, 12) - _ema(c, 26)
    ps = _ema(pm, 9)
    m1, m2 = macd.shift(1), macd.shift(2)
    cross = (macd > sig) & (m1 <= sig.shift(1))
    long_c = cross & (macd > m1) & (macd > m2)
    short_c = (macd < m1) & (macd < sig) & (pm < ps) & (lo < lo.shift(1)) & (lo < lo.shift(2))
    ix = bars_df.index
    false = pd.Series(False, index=ix)
    return long_c.fillna(False).astype(bool), false, short_c.fillna(False).astype(bool), false.copy()


def portfolio_kwargs(**params):
    return {}
