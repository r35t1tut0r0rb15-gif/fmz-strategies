"""Hourly bars, long only: the EMA 50 at or above the EMA 200, a green bar closing at or above the session VWAP, and any of the last 10 closes under the current lower Bollinger band (20 x 2) go long; the close crossing over the upper band closes (the 5 % stop names a non-existent entry and never acts).
Port of FMZ strategy #437661 "基于布林带和VWAP的量化交易策略Bollinger-Bands-and-VWAP-based-Quantitative-Trading-Strategy" (VWAP and BB strategy [EEMANI] (mohanee)).

FMZ source id: 437661

Source
    https://www.fmz.com/strategy/437661 (PineScript v4, FMZ last modified 2024-01-04 15:59:46).
    Verbatim copy: original_source.md. Read 2026-10-23 (FMZ-C).

Original signal (original_source.md lines 132-236), EMA 50 / 200; BB 20 x 2 of close; VWAP session; stop loss 5 %; pyramiding 2
    longCondition = ema50 >= ema200 and close >= vwap(close) and close > open;  is_price_dipped_bb(10, lowerBand) = any close[1 .. 10] < lowerBand (the current band)
    entry VWAP_BB LE;  crossover(close, upperBand) -> close VWAP_BB LE;  close(id = "VB LE") when close < avg x 0.95 (no such entry)

Interpretation choices (Pine rules in SURVEY_README.md)
    * The dip test compares the last 10 closes with the CURRENT lower band, as written. The stop-loss
      close uses the id "VB LE" while the entry is "VWAP_BB LE", so it never acts (weird case); not
      ported. pyramiding 2 lets a repeated signal add a second unit while long: adds are sizing, the port
      keeps one position (as earlier ports). vwap(close) is the session VWAP, anchored at the broker-day
      start (as earlier ports). Long only. 3 fixed units are sizing. FREQ = "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, EMA uptrend dip-and-recovery entries with a band exit.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: strategy(): fixed qty 3, pyramiding 2 (adds), capital 10000, not ported.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: used: the bars' volume column (broker tick volume of the cTrader M1 data, summed per bar) in the session VWAP of the close; exchange volume to be compared later (Austin, 2026-10-23).
Session open: VWAP anchored at the broker-day start.
Long only.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_437661_ema_uptrend_vwap_bb_dip_upper_band_exit_long"
FAMILY = "bollinger_reversion"  # proposed 2026-10-23 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "bb_len": [20, 50],
    "dip_bars": [10, 5],
}
DEFAULT_PARAMS = {"bb_len": 20, "mult": 2.0, "dip_bars": 10, "fast": 50, "slow": 200}


def _resample(raw_1m_df, freq):
    ohlcv = raw_1m_df[["open", "high", "low", "close", "volume"]]
    bars = ohlcv.resample(freq, label="left", closed="left").agg(
        {"open": "first", "high": "max", "low": "min", "close": "last", "volume": "sum"})
    bars = bars.dropna(subset=["close"])  # an empty period is not a bar; never forward-filled
    if bars.index.tz is None:
        raise ValueError("raw_1m_df must have a tz-aware UTC index")
    return bars


def precompute(raw_1m_df, symbol_key, **params):
    return _resample(raw_1m_df, FREQ)


def broker_day(index):
    """Broker day of each timestamp: the session ending 17:00 America/New_York, labelled by its
    end date (as worker A's ports). The desktop binds this name to registry_schema.broker_day."""
    ny = index.tz_convert("America/New_York")
    return (ny + pd.Timedelta(hours=7)).normalize().tz_localize(None)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    o, c, v = bars_df["open"], bars_df["close"], bars_df["volume"]
    day = broker_day(c.index)
    cv = v.groupby(day).cumsum()
    vwap = (c * v).groupby(day).cumsum() / cv.where(cv != 0)
    n = int(p["bb_len"])
    basis = c.rolling(n).mean()
    dev = float(p["mult"]) * c.rolling(n).std(ddof=0)
    upper, lower = basis + dev, basis - dev
    k = int(p["dip_bars"])
    dipped = np.logical_or.reduce([(c.shift(j) < lower).to_numpy() for j in range(1, k + 1)])
    trend = c.ewm(span=int(p["fast"]), adjust=False).mean() >= c.ewm(span=int(p["slow"]), adjust=False).mean()
    ent = (trend & (c >= vwap) & (c > o)).to_numpy() & dipped
    ext = ((c > upper) & (c.shift(1) <= upper.shift(1))).to_numpy()
    m = len(ent)
    le, lx = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    pos = 0
    for i in range(m):
        if pos == 0 and ent[i]:
            le[i], pos = True, 1
        elif pos == 1 and ext[i]:
            lx[i], pos = True, 0
    ix = bars_df.index
    false = pd.Series(False, index=ix)
    return pd.Series(le, index=ix), pd.Series(lx, index=ix), false, false.copy()


def portfolio_kwargs(**params):
    return {}
