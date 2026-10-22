"""States of the close against an SMA-based cloud and the EMA 200 with MACD agreeing, broker days: above span A and the EMA 200 with MACD over its signal goes long, below span B and the EMA 200 with MACD under goes short; reversing. The 1.5 / 3 ATR exit bracket is sent from the latest close on every exit-condition bar and is not ported (pending).
Port of FMZ strategy #478748 "多维度趋势判断与ATR动态止盈止损策略-Multi-Dimensional-Trend-Analysis-with-ATR-Based-Dynamic-Stop-Management-Strategy" (JOJO长趋势).

FMZ source id: 478748

Source
    https://www.fmz.com/strategy/478748 (PineScript v6, FMZ last modified 2025-01-17 16:39:21).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 79-145), "Ichimoku" as SMA 9 of highs / SMA 26 of lows; span B = SMAs 52 of high and low; MACD 12 / 26 / 9; EMA 200; exit bracket 1.5 / 3 x ATR 14
    close > spanA and macd > signal and close > ema200 -> entry Long;  close < spanB and macd < signal and close < ema200 -> entry Short
    exitLong = macd < signal or close < spanB -> exit(Long, stop = close - 1.5 atr, limit = close + 3 atr);  exitShort mirror

Interpretation choices (Pine rules in SURVEY_README.md)
    * The lines are simple moving averages of highs and lows, as written. The conditions are states and
      repeat; a repeat on the held side is ignored. The exit bracket is sent only on bars where its
      condition holds, each time from that bar's close and ATR, so its levels move while the condition
      lasts: stops() cannot express a level re-set every bar, so it is described here and kept pending
      (as #438034, mark trailing_stop_pending); positions end at the opposite entry until then. REVERSAL
      INTENDED. No sizing code. Daily bars are broker days (17:00 America/New_York), stamped with their
      first minute. FREQ = "1D" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; per-bar exit bracket described (pending).
    2 generic: PASS, SMA-cloud, MACD and EMA 200 trend states.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: the ATR bracket inputs stored.
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

NAME = "fmz_478748_sma_cloud_macd_ema200_state_reversal"
FAMILY = "ichimoku"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "conv_len": [9, 20],
    "base_len": [26, 50],
}
DEFAULT_PARAMS = {"conv_len": 9, "base_len": 26, "span_b_len": 52}


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
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    conv = h.rolling(int(p["conv_len"])).mean()
    base = lo.rolling(int(p["base_len"])).mean()
    span_a = (conv + base) / 2
    n = int(p["span_b_len"])
    span_b = (h.rolling(n).mean() + lo.rolling(n).mean()) / 2
    macd = c.ewm(span=12, adjust=False).mean() - c.ewm(span=26, adjust=False).mean()
    sig = macd.ewm(span=9, adjust=False).mean()
    e200 = c.ewm(span=200, adjust=False).mean()
    le = (c > span_a) & (macd > sig) & (c > e200)
    se = (c < span_b) & (macd < sig) & (c < e200)
    false = pd.Series(False, index=c.index)
    return le, false, se, false.copy()


def portfolio_kwargs(**params):
    return {}
