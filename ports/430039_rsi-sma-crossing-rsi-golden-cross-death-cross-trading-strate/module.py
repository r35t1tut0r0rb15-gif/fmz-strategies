"""RSI recovery under the SMA 200, broker days, long only: with the close below its SMA 200, RSI 14 crossing up through
30 goes long; with the close above the SMA 200, RSI 14 crossing down through 70 closes the long.
Port of FMZ strategy #430039 "均线穿越RSI金叉死叉交易策略SMA-Crossing-RSI-Golden-Cross-Death-Cross-Trading-Strategy" (Meu Robo com MA e RSI (Regras Especificas)).

FMZ source id: 430039

Source
    https://www.fmz.com/strategy/430039 (PineScript v4, FMZ last modified 2023-10-24 14:33:51).
    Verbatim copy: original_source.md. Read 2026-10-16 (FMZ-C).

Original signal (original_source.md lines 179-200), SMA 200, RSI 14, levels 30 / 70
    close < sma(close, 200) and crossover(rsi(close, 14), 30)  -> entry long
    close > sma(close, 200) and crossunder(rsi(close, 14), 70) -> close long

Interpretation choices (Pine rules in SURVEY_README.md)
    * Long only; the "venda" condition only closes the long. Opposite entries cannot occur.
    * Daily bars are broker days (17:00 America/New_York), stamped with their first minute.
      FREQ = "1D" from the backtest header (period 1d).

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, an RSI and a moving average.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: broker day (17:00 America/New_York, DST by the zone); no venue-open rule.
Long only. Opposite entries cannot occur.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_430039_rsi_recovery_below_sma200_long"
FAMILY = "rsi_oscillator"  # proposed 2026-10-16 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "rsi_len": [14, 7],
    "sma_len": [200, 100],
}
DEFAULT_PARAMS = {"rsi_len": 14, "sma_len": 200, "over_sold": 30, "over_bought": 70}


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


def _rsi(c, n):
    ch = c.diff()
    up = ch.clip(lower=0).ewm(alpha=1 / n, adjust=False).mean()
    dn = (-ch.clip(upper=0)).ewm(alpha=1 / n, adjust=False).mean()
    rsi = 100 - 100 / (1 + up / dn)
    rsi = rsi.where(up != 0, 0.0)
    return rsi.where(dn != 0, 100.0).where(ch.notna())


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    c = bars_df["close"]
    sma = c.rolling(int(p["sma_len"])).mean()
    r = _rsi(c, int(p["rsi_len"]))
    xo = (r > p["over_sold"]) & (r.shift(1) <= p["over_sold"])
    xu = (r < p["over_bought"]) & (r.shift(1) >= p["over_bought"])
    long_e = ((c < sma) & xo).astype(bool)
    long_x = ((c > sma) & xu).astype(bool)
    false = pd.Series(False, index=bars_df.index)
    return long_e, long_x, false, false.copy()


def portfolio_kwargs(**params):
    return {}
