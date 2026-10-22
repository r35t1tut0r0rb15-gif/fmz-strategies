"""Close against the SMA 52 with MACD 12 / 26 / 9 on the same side of zero and of its signal, broker days: the long state holds a long, the short state a short, and a bar in neither state closes; the 1 % stop and 2 % target are re-sent from each signal bar's close (pending); reversing.
Port of FMZ strategy #482678 "MACD结合阿尔布鲁克斯价格行为的趋势跟踪策略-MACD-Based-Al-Brooks-Price-Action-Trend-Following-Strategy" (Al Brooks Price Action with MACD Signals).

FMZ source id: 482678

Source
    https://www.fmz.com/strategy/482678 (PineScript v6, FMZ last modified 2025-02-19 17:36:15).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 107-160), SMA 52; MACD 12 / 26 / 9; stop 1 %, RR 2.0; candle type Close
    close > sma and macd > 0 and macd > signal -> entry Buy + exit(limit = close + 2 x 1 %, stop = close x 0.99);  mirror -> entry Sell + exit
    not buy and not sell -> close Sell, close Buy

Interpretation choices (Pine rules in SURVEY_README.md)
    * The signals are states, true on every bar they hold, and each one re-sends the bracket from that
      bar's close: stops() cannot express a level re-set every bar, so it is described here and kept
      pending (as #438034, mark trailing_stop_pending); positions end when neither state holds or at the
      opposite state. The candle type is the default Close. REVERSAL INTENDED. No sizing code. The source
      carries the Mozilla Public License 2.0 notice. Daily bars are broker days (17:00 America/New_York),
      stamped with their first minute. FREQ = "1D" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; re-sent bracket described (pending).
    2 generic: PASS, SMA side with MACD state.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: broker day (17:00 America/New_York, DST by the zone); no venue-open rule.
REVERSAL INTENDED.

Marks: trailing_stop_pending
"""
import numpy as np
import pandas as pd

NAME = "fmz_482678_sma52_side_macd_state_neutral_exit_reversal"
FAMILY = "macd"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "length": [52, 100],
    "macd_fast": [12, 8],
}
DEFAULT_PARAMS = {"length": 52, "macd_fast": 12, "macd_slow": 26, "macd_signal": 9}


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

    def ema(x, n):
        return x.ewm(span=int(n), adjust=False).mean()

    sma = c.rolling(int(p["length"])).mean()
    macd = ema(c, p["macd_fast"]) - ema(c, p["macd_slow"])
    sig = ema(macd, p["macd_signal"])
    buy = (c > sma) & (macd > 0) & (macd > sig)
    sell = (c < sma) & (macd < 0) & (macd < sig)
    neutral = ~buy & ~sell
    return buy, neutral, sell, neutral.copy()


def portfolio_kwargs(**params):
    return {}
