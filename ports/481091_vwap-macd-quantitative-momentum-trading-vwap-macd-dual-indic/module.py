"""2-hour bars: the MACD (12 / 26 / 9) crossing over its signal with the close above the session VWAP goes long, crossing under with the close below goes short; a long closes on a MACD crossing under or a close under the VWAP, a short on the mirror; reversing.
Port of FMZ strategy #481091 "量化动量交易VWAP-MACD双指标趋势跟踪策略-Quantitative-Momentum-Trading-VWAP-MACD-Dual-Indicator-Trend-Following-Strategy" (VWAP + MACD Strategy).

FMZ source id: 481091

Source
    https://www.fmz.com/strategy/481091 (PineScript v5, FMZ last modified 2025-02-08 14:45:43).
    Verbatim copy: original_source.md. Read 2026-10-23 (FMZ-C).

Original signal (original_source.md lines 98-141), session VWAP; MACD 12 / 26 / 9; 200 % of equity
    longCondition = crossover(macd, signal) and close > vwap -> entry Long;  shortCondition = crossunder(macd, signal) and close < vwap -> entry Short
    exitLong = crossunder(macd, signal) or close < vwap -> close Long;  exitShort = crossover(macd, signal) or close > vwap -> close Short

Interpretation choices (Pine rules in SURVEY_README.md)
    * ta.vwap(close) restarts each session: the house session is the broker day (17:00
      America/New_York), so the VWAP is the volume-weighted close of the day's 2-hour bars so far, each
      bar placed in the broker day of its start. The closes act only on a position the bar's entries
      leave unchanged (from the bar after the fill); an opposite entry reverses. REVERSAL INTENDED. 200 %
      of equity is sizing. FREQ = "2h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, MACD crossings on the session-VWAP side with VWAP exits.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: 200 % of equity stored, not ported.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: used: the bars' volume column (broker tick volume of the cTrader M1 data, summed per bar) as the session-VWAP weights; exchange volume to be compared later (Austin, 2026-10-23).
Session open: broker day (17:00 America/New_York, DST by the zone) for the VWAP reset; no venue-open rule.
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_481091_macd_cross_session_vwap_side_exit_2h_reversal"
FAMILY = "vwap"  # proposed 2026-10-23 (FMZ-C), user to confirm
FREQ = "2h"  # backtest header period: 2h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "fast": [12, 8],
    "slow": [26, 21],
}
DEFAULT_PARAMS = {"fast": 12, "slow": 26, "signal": 9}


def broker_day(index):
    """Broker day of each timestamp: the session ending 17:00 America/New_York, labelled by its
    end date (as worker A's ports). The desktop binds this name to registry_schema.broker_day."""
    ny = index.tz_convert("America/New_York")
    return (ny + pd.Timedelta(hours=7)).normalize().tz_localize(None)


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


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    c, v = bars_df["close"], bars_df["volume"]
    day = broker_day(bars_df.index)
    vw = (c * v).groupby(day).cumsum() / v.groupby(day).cumsum()
    macd = c.ewm(span=int(p["fast"]), adjust=False).mean() - c.ewm(span=int(p["slow"]), adjust=False).mean()
    sig = macd.ewm(span=int(p["signal"]), adjust=False).mean()
    xo = (macd > sig) & (macd.shift(1) <= sig.shift(1))
    xu = (macd < sig) & (macd.shift(1) >= sig.shift(1))
    buy, sell = (xo & (c > vw)).to_numpy(), (xu & (c < vw)).to_numpy()
    ex_l, ex_s = (xu | (c < vw)).to_numpy(), (xo | (c > vw)).to_numpy()
    m = len(buy)
    le, lx = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    se, sx = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    pos = 0
    for i in range(m):
        new = pos
        if buy[i] and new != 1:
            new = 1
        if sell[i] and new != -1:
            new = -1
        if new == pos:
            if pos == 1 and ex_l[i]:
                new = 0
            elif pos == -1 and ex_s[i]:
                new = 0
        if new != pos:
            if new == 1:
                le[i] = True
            elif new == -1:
                se[i] = True
            elif pos == 1:
                lx[i] = True
            else:
                sx[i] = True
            pos = new
    ix = bars_df.index
    return (pd.Series(le, index=ix), pd.Series(lx, index=ix),
            pd.Series(se, index=ix), pd.Series(sx, index=ix))


def portfolio_kwargs(**params):
    return {}
