"""EMA 12 / 25 trend flips counted bar by bar, daily bars: the first bar of the EMA 12 above the EMA 25 goes long, the first bar below goes short; reversing (the stochastic RSI block only colours and
alerts).
Port of FMZ strategy #444040 "基于EMA和随机RSI的多周期趋势跟踪交易策略EMA-and-Stochastic-RSI-based-Multi-timeframe-Trend-Following-Trading-Strategy" ([Jacky] Trader XO Macro Trend Scanner).

FMZ source id: 444040

Source
    https://www.fmz.com/strategy/444040 (PineScript v5, FMZ last modified 2024-03-08 17:32:38).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 169-304), EMA 12 / 25 (consolidated 25); stochastic RSI 14 / 14 / 3 / 3 and MA 200 (alerts only)
    countBuy counts bars with ema12 > ema25 (reset on a bar below), countSell the mirror;  buysignal = countBuy == 1 and countSell == 0 and buy and not buy[1] -> entry Buy;  sellsignal mirrored -> entry Sell

Interpretation choices (Pine rules in SURVEY_README.md)
    * The counters make each signal the first bar of a new EMA order, as written. The stochastic RSI,
      band and MA blocks only colour the chart and raise alerts. strategy.entry reverses: REVERSAL
      INTENDED. No sizing code. FREQ = "1D" from the backtest header (broker days).

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, EMA order flips.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_444040_xo_ema12_25_first_bar_flip_reversal"
FAMILY = "ma_cross"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "fast": [12, 9],
    "slow": [25, 50],
}
DEFAULT_PARAMS = {"fast": 12, "slow": 25}


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
    f = c.ewm(span=int(p["fast"]), adjust=False).mean().to_numpy()
    s = c.ewm(span=int(p["slow"]), adjust=False).mean().to_numpy()
    buy, sell = f > s, f < s
    m = len(c)
    le, se = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    cb = cs = 0
    for i in range(m):
        if buy[i]:
            cb, cs = cb + 1, 0
        if sell[i]:
            cs, cb = cs + 1, 0
        b1 = buy[i - 1] if i > 0 else False
        s1 = sell[i - 1] if i > 0 else False
        le[i] = cb == 1 and cs == 0 and buy[i] and not b1
        se[i] = cs == 1 and cb == 0 and sell[i] and not s1
    ix = bars_df.index
    false = pd.Series(False, index=ix)
    return pd.Series(le, index=ix), false, pd.Series(se, index=ix), false.copy()


def portfolio_kwargs(**params):
    return {}
