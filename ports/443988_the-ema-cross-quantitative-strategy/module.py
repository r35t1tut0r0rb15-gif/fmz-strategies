"""Close above an EMA 200, daily bars, long only: from flat, the close above the EMA 200 goes long; the close under the EMA 10, or 10 % under the fill, closes.
Port of FMZ strategy #443988 "The EMA Cross Quantitative Strategy" (EMA strategy (ZenAndTheArtOfTrading)).

FMZ source id: 443988

Source
    https://www.fmz.com/strategy/443988 (PineScript v5, FMZ last modified 2024-03-08 14:18:21).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 134-183), EMA 200 / 10; stop 10 %; exit on lower close off; 100 % of equity, capital 50000, commission 0.005 per contract
    flat and close > ema200 -> entry Long;  buyCondition[1] -> buyPrice = open;  long and close < ema10 -> close;  long and (buyPrice - close) / close > 0.10 -> close

Interpretation choices (Pine rules in SURVEY_README.md)
    * buyPrice is the open of the bar after the signal, the fill price; the stop is a bar-close test
      against it, filled at the next open. The date filter is set to true. Long only. The 100 % of
      equity size, capital and per-contract commission are sizing and costs. FREQ = "1D" from the
      backtest header (broker days).

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, EMA trend entry with an EMA 10 and fill-price exit.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: the percent-of-equity size, capital and commission stored.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: ND438794 (2 members, best partner #438794, Jaccard 0.717); ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
Long only.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_443988_ema200_trend_ema10_exit_fill_stop_long"
FAMILY = "ma_trend"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "ma1": [200, 100],
    "ma2": [10, 20],
}
DEFAULT_PARAMS = {"ma1": 200, "ma2": 10, "stop_pct": 0.10}


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
    o, c = bars_df["open"], bars_df["close"]
    e1 = c.ewm(span=int(p["ma1"]), adjust=False).mean()
    e2 = c.ewm(span=int(p["ma2"]), adjust=False).mean()
    go = (c > e1).to_numpy()
    out = (c < e2).to_numpy()
    cv, ov = c.to_numpy(dtype=float), o.to_numpy(dtype=float)
    sp = float(p["stop_pct"])
    m = len(cv)
    le, lx = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    held, fill = False, np.nan
    for i in range(m):
        if go[i] and not held:
            le[i] = True
            if i + 1 < m:
                fill = ov[i + 1]
        elif held and (out[i] or (fill - cv[i]) / cv[i] > sp):
            lx[i] = True
        held = (held and not lx[i]) or le[i]
    ix = bars_df.index
    false = pd.Series(False, index=ix)
    return pd.Series(le, index=ix), pd.Series(lx, index=ix), false, false.copy()


def portfolio_kwargs(**params):
    return {}
