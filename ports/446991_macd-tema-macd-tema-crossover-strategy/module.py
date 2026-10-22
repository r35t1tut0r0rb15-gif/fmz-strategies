"""A MACD built from triple EMAs (TEMA 12 minus TEMA 26) crossing its TEMA-9 signal, daily bars: crossing up goes long, crossing down goes short; reversing.
Port of FMZ strategy #446991 "MACD-TEMA-交叉策略-MACD-TEMA-Crossover-Strategy" (MACD TEMA Strategy).

FMZ source id: 446991

Source
    https://www.fmz.com/strategy/446991 (PineScript v4, FMZ last modified 2024-04-03 18:25:32).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 94-143), TEMA 12 / 26 (inputs titled short / long); signal TEMA 9
    tema(n) = 3 ema - 3 ema(ema) + ema(ema(ema));  macd = tema(close, 12) - tema(close, 26);  signal = tema(macd, 9);  crossover -> entry Buy;  crossunder -> entry Sell

Interpretation choices (Pine rules in SURVEY_README.md)
    * The input names swap "short" and "long", but the values give TEMA 12 minus TEMA 26, the usual
      sign. No exit: positions end at the opposite entry. strategy.entry reverses: REVERSAL INTENDED. No
      sizing code. FREQ = "1D" from the backtest header (broker days).

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, TEMA-MACD signal crossings.
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

NAME = "fmz_446991_tema_macd_signal_cross_reversal"
FAMILY = "macd_cross"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
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


def _ema(x, n):
    return x.ewm(span=int(n), adjust=False).mean()


def _tema(x, n):
    e1 = _ema(x, n)
    e2 = _ema(e1, n)
    return 3 * e1 - 3 * e2 + _ema(e2, n)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    c = bars_df["close"]
    macd = _tema(c, p["fast"]) - _tema(c, p["slow"])
    sig = _tema(macd, p["signal"])
    le = (macd > sig) & (macd.shift(1) <= sig.shift(1))
    se = (macd < sig) & (macd.shift(1) >= sig.shift(1))
    false = pd.Series(False, index=bars_df.index)
    return le, false, se, false.copy()


def portfolio_kwargs(**params):
    return {}
