"""A "market sentiment" line (EMA 49 of the close change over EMA 49 of volume) run through a MACD (EMA 40 / 204, signal 20), broker days, long only: the histogram crossing over zero buys from flat, the MACD crossing under zero closes.
Port of FMZ strategy #361332 "Sentiment Oscillator" (Sentiment Oscillator with Backtest).

FMZ source id: 361332

Source
    https://www.fmz.com/strategy/361332 (PineScript v4, FMZ last modified 2022-05-05 20:45:11).
    Verbatim copy: original_source.md. Read 2026-10-23 (FMZ-C).

Original signal (original_source.md lines 55-205), sentiment 49; EMA 40 / 204; signal 20; defaults: entry Histogram crossing over Zero Line, exit MACD crossing under Zero Line
    marketSentiment = ema(close - close[1], 49) / ema(volume, 49) x 1e9;  macd = ema(ms, 40) - ema(ms, 204);  signal = ema(macd, 20);  hist = macd - signal
    crossover(hist, 0) -> entry Buy;  crossunder(macd, 0) -> close Buy

Interpretation choices (Pine rules in SURVEY_README.md)
    * The menus take their defaults (the alternate change-per-volume method is off). An entry and a close
      can both be true on one bar: the entry comes first, so from flat the entry stands and the close does
      not act on it; when a long is held into the bar the entry is ignored and the close acts (as
      #441963): a loop. Long only. No sizing code. The source carries the Mozilla Public License 2.0
      notice. Daily bars are broker days (17:00 America/New_York), stamped with their first minute.
      FREQ = "1D" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, MACD of a price-change / volume sentiment line.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: used: the bars' volume column (broker tick volume of the cTrader M1 data, summed per bar) as the divisor EMA(volume, 49) of the sentiment line; exchange volume to be compared later (Austin, 2026-10-23).
Session open: broker day (17:00 America/New_York, DST by the zone); no venue-open rule.
Long only.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_361332_change_per_volume_sentiment_macd_hist_zero_long"
FAMILY = "macd_momentum"  # proposed 2026-10-23 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "ms_len": [49, 20],
    "ema_len2": [204, 100],
}
DEFAULT_PARAMS = {"ms_len": 49, "ema_len2": 204, "ema_len1": 40, "signal_len": 20}


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


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    c, v = bars_df["close"], bars_df["volume"]

    def ema(x, n):
        return x.ewm(span=int(n), adjust=False).mean()

    n = int(p["ms_len"])
    ve = ema(v, n)
    ms = ema(c.diff(), n) / ve.where(ve != 0) * 1e9
    macd = ema(ms, p["ema_len1"]) - ema(ms, p["ema_len2"])
    hist = macd - ema(macd, p["signal_len"])
    lc = ((hist > 0) & (hist.shift(1) <= 0)).to_numpy()
    xc = ((macd < 0) & (macd.shift(1) >= 0)).to_numpy()
    m = len(lc)
    le, lx = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    pos = 0
    for i in range(m):
        if pos == 1 and xc[i]:
            lx[i], pos = True, 0                  # the close acts on the long held into the bar
        elif pos == 0 and lc[i]:
            le[i], pos = True, 1
    ix = bars_df.index
    false = pd.Series(False, index=ix)
    return pd.Series(le, index=ix), pd.Series(lx, index=ix), false, false.copy()


def portfolio_kwargs(**params):
    return {}
