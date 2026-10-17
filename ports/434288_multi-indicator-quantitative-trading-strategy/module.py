"""Configurable tester with its defaults, 2-hour bars, long only: while the SMA 50 is above the SMA 100 the strategy is
long; when the SMA 50 is at or below the SMA 100 it closes. The default RSI filters (0-100, also on the daily RSI) always
pass.
Port of FMZ strategy #434288 "Multi Indicator Quantitative Trading Strategy" (Strategy Tester EMA-SMA-RSI-MACD (Strat-test)).

FMZ source id: 434288

Source
    https://www.fmz.com/strategy/434288 (PineScript v4, FMZ last modified 2023-12-05 10:29:20).
    Verbatim copy: original_source.md. Read 2026-10-17 (FMZ-C).

Original signal (original_source.md lines 253-499), defaults: source close; type Long Only; entry "(E)MA 1 > (E)MA 2" (SMA 50 / 100); exit "(E)MA 3 < (E)MA 4" (SMA 50 / 100); extras none; RSI 0-100; SL / TP off
    BUY = sma50 > sma100 and RSI (rsi > 0 and <= 100 and daily rsi > 0 and <= 100);  SELL = sma50 <= sma100 and RSI
    BUY -> entry long ("[B]");  SELL -> close long (Long Only)

Interpretation choices (Pine rules in SURVEY_README.md)
    * Only the defaults are ported: every other menu choice is a different strategy. The RSI gate
      (0 < RSI <= 100 on the chart and on the daily RSI) is true whenever the RSIs are defined; the
      daily RSI (security 'D' without lookahead) is read from the last completed broker day.
    * The entry is a level (ignored while long). Long only; Opposite entries cannot occur. FREQ =
      "2h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; daily value from completed broker days.
    2 generic: PASS, moving-average order and RSI bounds.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: the strategy() 100 % of equity stored.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: daily RSI on broker days (17:00 America/New_York, DST by the zone); no venue-open rule.
Long only. Opposite entries cannot occur.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_434288_sma_50_100_state_long"
FAMILY = "ma_trend"  # proposed 2026-10-17 (FMZ-C), user to confirm
FREQ = "2h"  # backtest header period: 2h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "len1": [50, 20],
    "len2": [100, 200],
}
DEFAULT_PARAMS = {"len1": 50, "len2": 100, "rsi_len": 20}


def broker_day(index):
    """Broker day of each timestamp: the session ending 17:00 America/New_York, labelled by its
    end date (as worker A's ports). The desktop binds this name to registry_schema.broker_day."""
    ny = index.tz_convert("America/New_York")
    return (ny + pd.Timedelta(hours=7)).normalize().tz_localize(None)


def _resample(raw_1m_df, freq):
    ohlc = raw_1m_df[["open", "high", "low", "close"]]
    bars = ohlc.resample(freq, label="left", closed="left").agg(
        {"open": "first", "high": "max", "low": "min", "close": "last"})
    bars = bars.dropna(how="all")  # an empty period is not a bar; never forward-filled
    if bars.index.tz is None:
        raise ValueError("raw_1m_df must have a tz-aware UTC index")
    return bars


def _rsi(c, n):
    ch = c.diff()
    up = ch.clip(lower=0).ewm(alpha=1 / n, adjust=False).mean()
    dn = (-ch.clip(upper=0)).ewm(alpha=1 / n, adjust=False).mean()
    return (100 - 100 / (1 + up / dn)).where(up != 0, 0.0).where(dn != 0, 100.0).where(up.notna())


def precompute(raw_1m_df, symbol_key, **params):
    return _resample(raw_1m_df, FREQ)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    c = bars_df["close"]
    a = c.rolling(int(p["len1"])).mean()
    b = c.rolling(int(p["len2"])).mean()
    n = int(p["rsi_len"])
    r = _rsi(c, n)
    day = broker_day(bars_df.index)
    dc = pd.Series(c.to_numpy(), index=day).groupby(level=0).last()
    rd = pd.Series(_rsi(dc, n).shift(1).reindex(day).to_numpy(), index=c.index)
    gate = (r > 0) & (r <= 100) & (rd > 0) & (rd <= 100)
    buy = ((a > b) & gate).to_numpy()
    sell = ((a <= b) & gate).to_numpy()
    m = len(c)
    tgt = np.zeros(m, dtype=np.int8)
    pos = 0
    for i in range(m):
        if pos == 0 and buy[i]:
            pos = 1
        elif pos == 1 and sell[i]:
            pos = 0
        tgt[i] = pos
    prev = np.concatenate(([0], tgt[:-1]))
    ix = bars_df.index
    false = pd.Series(False, index=ix)
    return (pd.Series((tgt == 1) & (prev == 0), index=ix), pd.Series((prev == 1) & (tgt == 0), index=ix),
            false, false.copy())


def portfolio_kwargs(**params):
    return {}
