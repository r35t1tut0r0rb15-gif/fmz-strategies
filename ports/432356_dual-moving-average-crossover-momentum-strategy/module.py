"""MACD histogram growth above zero, broker days: the histogram (12 / 26 / 9) above zero and rising goes long, above zero
and falling goes short; an unchanged histogram keeps the previous colour; always in once started.
Port of FMZ strategy #432356 "Dual Moving Average Crossover Momentum Strategy" (Histogram MacD MVP_V2.1).

FMZ source id: 432356

Source
    https://www.fmz.com/strategy/432356 (PineScript v5, FMZ last modified 2023-11-16 17:25:13).
    Verbatim copy: original_source.md. Read 2026-10-17 (FMZ-C).

Original signal (original_source.md lines 249-344), MACD 12 / 26 / 9 (EMA), indicator timeframe = chart
    histA_IsUp := hist == hist[1] ? histA_IsUp[1] : hist > hist[1] and hist > 0;  histA_IsDown likewise with hist < hist[1] and hist > 0
    histA_IsUp -> entry long;  histA_IsDown -> entry short

Interpretation choices (Pine rules in SURVEY_README.md)
    * The indicator timeframe input is empty, i.e. the chart's own: request.security on the same
      timeframe adds nothing. The histogram is MACD minus its EMA 9 signal, as written. Below zero
      neither entry fires, so the position is held. The alerts and colours only draw.
    * strategy.entry reverses: REVERSAL INTENDED. Daily bars are broker days (17:00 America/New_York),
      stamped with their first minute. FREQ = "1D" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, MACD histogram sign and slope.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: ND364540 (2 members, best partner #364540, Jaccard 0.770); ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: broker day (17:00 America/New_York, DST by the zone); no venue-open rule.
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_432356_macd_histogram_growth"
FAMILY = "macd_momentum"  # proposed 2026-10-17 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "fast": [12, 8],
    "slow": [26, 17],
}
DEFAULT_PARAMS = {"fast": 12, "slow": 26, "signal": 9}


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
    macd = c.ewm(span=int(p["fast"]), adjust=False).mean() - c.ewm(span=int(p["slow"]), adjust=False).mean()
    hist = (macd - macd.ewm(span=int(p["signal"]), adjust=False).mean()).to_numpy()
    m = len(hist)
    tgt = np.zeros(m, dtype=np.int8)
    a_up = a_dn = False
    pos = 0
    for i in range(1, m):
        if hist[i] != hist[i - 1]:
            a_up = hist[i] > hist[i - 1] and hist[i] > 0
            a_dn = hist[i] < hist[i - 1] and hist[i] > 0
        if a_up:
            pos = 1
        if a_dn:
            pos = -1
        tgt[i] = pos
    prev = np.concatenate(([0], tgt[:-1]))
    le = (tgt == 1) & (prev != 1)
    se = (tgt == -1) & (prev != -1)
    false = np.zeros(m, dtype=bool)
    return tuple(pd.Series(a, index=bars_df.index) for a in (le, false, se, false.copy()))


def portfolio_kwargs(**params):
    return {}
