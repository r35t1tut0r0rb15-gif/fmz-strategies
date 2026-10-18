"""CCI breakout signals that alternate on a latch, broker days, long only: with the CCI 14 over +100 the buy condition is true on every other bar
(the latch resets each bar it fires); the CCI under -100 closes the long on the same alternating pattern.
Port of FMZ strategy #435724 "基于CCI指标的长线交易策略CCI-Long-Only-Strategy" (CCI Long Only Strategy).

FMZ source id: 435724

Source
    https://www.fmz.com/strategy/435724 (PineScript v5, FMZ last modified 2023-12-18 12:32:07).
    Verbatim copy: original_source.md. Read 2026-10-18 (FMZ-C).

Original signal (original_source.md lines 113-137), CCI 14, levels +100 / -100
    buyCondition = cci > 100 and na(lastBuySignal);  lastBuySignal := buyCondition ? true : na;  sellCondition = cci < -100 and na(lastSellSignal);  lastSellSignal := sellCondition ? true : na
    buyCondition -> entry long;  sellCondition -> close long

Interpretation choices (Pine rules in SURVEY_README.md)
    * The latch is true only on the bar after a firing, so while the CCI stays over 100 the buy
      condition is true, false, true, false, ... (as written); the same for the sell condition. An entry
      while long adds nothing. Long only. Daily bars are broker days (17:00 America/New_York),
      stamped with their first minute. FREQ = "1D" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, CCI levels.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (3 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: broker day (17:00 America/New_York, DST by the zone); no venue-open rule.
Long only.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_435724_cci_alternating_latch_long"
FAMILY = "cci_oscillator"  # proposed 2026-10-18 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "cci_period": [14, 20, 28],
}
DEFAULT_PARAMS = {"cci_period": 14, "level": 100.0}


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


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    c = bars_df["close"]
    n = int(p["cci_period"])
    ma = c.rolling(n).mean()
    md = c.rolling(n).apply(lambda a: np.mean(np.abs(a - a.mean())), raw=True)
    with np.errstate(invalid="ignore", divide="ignore"):
        cci = ((c - ma) / (0.015 * md)).to_numpy()
    lv = float(p["level"])
    m = len(cci)
    le, lx = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    last_buy = last_sell = False
    for i in range(m):
        buy = bool(cci[i] > lv) and not last_buy
        sell = bool(cci[i] < -lv) and not last_sell
        last_buy, last_sell = buy, sell
        le[i], lx[i] = buy, sell
    ix = bars_df.index
    false = pd.Series(False, index=ix)
    return pd.Series(le, index=ix), pd.Series(lx, index=ix), false, false.copy()


def portfolio_kwargs(**params):
    return {}
