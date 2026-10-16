"""Welles Wilder's trend balance point, 5-minute bars: when the previous bar's 2-bar momentum is above
both earlier ones go long, below both go short; each position has a take-profit and a stop-loss.
Port of FMZ strategy #427674 "Welles Wilder's Trend Balance Point System" (X-Trader.net).

FMZ source id: 427674

Source
    https://www.fmz.com/strategy/427674 (PineScript v3, FMZ last modified 2023-09-23 15:30:58).
    Verbatim copy: original_source.md. Read 2026-10-16 (FMZ-C).

Original signal (original_source.md lines 222-245), momentum period 2
    longTrigger = mom[1] > mom[2] and mom[1] > mom[3]; shortTrigger mirrors
    longEntry = not long and longTrigger (shortEntry mirrors) -> entry
    longStop = hlc3[1] - range[1]; longTP = 2 hlc3[1] - low[1] (prices, valuewhen at the entry signal)
    exit(profit = longTP, loss = longStop) -- PRICES passed as TICK distances

Interpretation choices (Pine rules in SURVEY_README.md)
    * AS WRITTEN: `profit` and `loss` take tick counts, so the bracket distances are the price
      levels times the tick size, i.e. about (tick size) x price: on the source's BTC_USDT (tick
      0.1) about 10 % of the price on each side. Ported as a symmetric percent bracket
      `bracket_pct` (default 10, as the source on BTC). Decision owed: the intended version is
      stop / limit at the Wilder levels themselves.
    * Criterion 2: the tick-size dependence is replaced by a percentage (stated before any backtest).
    * Stop module: portfolio_kwargs {} (driver D4); REVERSAL INTENDED.
    * FREQ = "5min" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; bracket fixed at entry.
    2 generic: ADAPT, tick-scaled distances -> percentages.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: 100 % of equity stored; the bracket quoted in original_sizing.txt.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
REVERSAL INTENDED.

Marks: none
"""
import pandas as pd

NAME = "fmz_427674_wilder_trend_balance_point"
FAMILY = "momentum_breakout"  # proposed 2026-10-16 (FMZ-C), user to confirm
FREQ = "5min"  # backtest header period: 5m
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "mom_per": [2, 4],
    "bracket_pct": [10.0, 2.0],
}
DEFAULT_PARAMS = {"mom_per": 2, "bracket_pct": 10.0}


def _resample(raw_1m_df, freq):
    ohlc = raw_1m_df[["open", "high", "low", "close"]]
    bars = ohlc.resample(freq, label="left", closed="left").agg(
        {"open": "first", "high": "max", "low": "min", "close": "last"})
    bars = bars.dropna(how="all")  # an empty period is not a bar; never forward-filled
    if bars.index.tz is None:
        raise ValueError("raw_1m_df must have a tz-aware UTC index")
    return bars


def precompute(raw_1m_df, symbol_key, **params):
    return _resample(raw_1m_df, FREQ)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    c = bars_df["close"]
    mom = c - c.shift(int(p["mom_per"]))
    m1, m2, m3 = mom.shift(1), mom.shift(2), mom.shift(3)
    # the triggers themselves: Pine enters when not already on that side, and a house stop can
    # flatten a position, so a trigger after a stop-out re-enters (an entry while held is ignored)
    le = ((m1 > m2) & (m1 > m3)).astype(bool)
    se = ((m1 < m2) & (m1 < m3)).astype(bool)
    false = pd.Series(False, index=bars_df.index)
    return le, false, se, false.copy()


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    f = float(p["bracket_pct"]) / 100
    return {"sl_stop": f, "tp_stop": f}


def portfolio_kwargs(**params):
    return {}
