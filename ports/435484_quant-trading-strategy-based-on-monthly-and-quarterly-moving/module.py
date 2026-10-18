"""Monthly / quarterly average cross with a pullback filter, broker days, long only: the SMA 20 over the SMA 60 with the close
over 90 % of the 10-bar high goes long; it is closed when the close falls under 90 % of the 10-bar high, when the SMA 20
crosses under the SMA 60 (stands under), or when the close is 10 % under the entry price.
Port of FMZ strategy #435484 "Quant Trading Strategy Based on Monthly and Quarterly Moving Average Operation" (均線操作-月季).

FMZ source id: 435484

Source
    https://www.fmz.com/strategy/435484 (PineScript v4, FMZ last modified 2023-12-15 11:49:06).
    Verbatim copy: original_source.md. Read 2026-10-18 (FMZ-C).

Original signal (original_source.md lines 129-155), SMA 20 / 60; 10-bar high x 0.9; 10 % stop on the average price
    to_long = sma20 > sma60 and close > highest(10) 0.9;  to_exit = close < highest(10) 0.9;  to_close = sma20 < sma60;  to_stop = close < 0.9 position_avg_price
    to_long -> entry long;  to_exit / to_close / to_stop -> close

Interpretation choices (Pine rules in SURVEY_README.md)
    * highest(10) is the highest HIGH of 10 bars (Pine's one-argument form). The three exits are
      the script's own tests on bar closes, filled at the next open: close-based exit signals (no
      mark). The average price is the entry fill (the next open). While long, a still-true entry
      condition adds nothing; after an exit the entry is taken again on the next flat bar if the
      condition holds. The backtest start inputs are not used by the orders. The 30 % of equity size
      is sizing. Daily bars are broker days (17:00 America/New_York), stamped with their first
      minute. FREQ = "1D" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; exits on closes.
    2 generic: PASS, average cross, 10-bar high pullback and a percent stop on closes.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: the percent-of-equity size stored.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: broker day (17:00 America/New_York, DST by the zone); no venue-open rule.
Long only.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_435484_sma_20_60_pullback_long"
FAMILY = "ma_cross"  # proposed 2026-10-18 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "fast": [20, 10],
    "slow": [60, 50],
}
DEFAULT_PARAMS = {"fast": 20, "slow": 60, "hh_len": 10, "pull": 0.9, "stop": 0.9}


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
    o, h, c = bars_df["open"], bars_df["high"], bars_df["close"]
    s_f = c.rolling(int(p["fast"])).mean()
    s_s = c.rolling(int(p["slow"])).mean()
    hh = h.rolling(int(p["hh_len"])).max() * float(p["pull"])
    to_long = ((s_f > s_s) & (c > hh)).to_numpy()
    to_exit = (c < hh).to_numpy()
    to_close = (s_f < s_s).to_numpy()
    cv, ov = c.to_numpy(dtype=float), o.to_numpy(dtype=float)
    stop = float(p["stop"])
    m = len(cv)
    tgt = np.zeros(m, dtype=np.int8)
    pos, avg, pend = 0, np.nan, None
    for i in range(m):
        if pend == "enter":
            pos, avg = 1, ov[i]
        elif pend == "exit":
            pos, avg = 0, np.nan
        pend = None
        if pos == 0 and to_long[i]:
            pend = "enter"
        elif pos == 1 and (to_exit[i] or to_close[i] or cv[i] < stop * avg):
            pend = "exit"
        tgt[i] = 1 if (pend == "enter" or (pos == 1 and pend != "exit")) else 0
    prev = np.concatenate(([0], tgt[:-1]))
    ix = bars_df.index
    false = pd.Series(False, index=ix)
    return (pd.Series((tgt == 1) & (prev != 1), index=ix), pd.Series((tgt == 0) & (prev == 1), index=ix),
            false, false.copy())


def portfolio_kwargs(**params):
    return {}
