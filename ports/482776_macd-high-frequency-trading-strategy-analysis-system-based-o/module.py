"""Hourly bars: a close back above the lower Bollinger band (20, 2) after a close under it, with MACD above its signal and volume at least its 20-bar average, goes long; the mirror at the upper band goes short; at most 5 signals per broker day; each trade has a 2 % stop and a 4 % target from its fill; reversing.
Port of FMZ strategy #482776 "基于布林带和MACD指标的高频交易策略分析系统-High-Frequency-Trading-Strategy-Analysis-System-Based-on-Bollinger-Bands-and-MACD-Indicators" (Bollinger Bounce Reversal Strategy - Visual Edition).

FMZ source id: 482776

Source
    https://www.fmz.com/strategy/482776 (PineScript v5, FMZ last modified 2025-02-20 17:55:49).
    Verbatim copy: original_source.md. Read 2026-10-23 (FMZ-C).

Original signal (original_source.md lines 93-189), BB 20 x 2; MACD 12 / 26 / 9; volume SMA 20 x 1.0; max 5 trades a day; SL 2 %, TP 4 % of position_avg_price; 5 % of equity
    longSignal = close[1] < lowerBB and close > lowerBB and macd > signal and volume >= volAvg;  longSignal and tradesToday < 5 -> entry Long, tradesToday += 1  (short mirrored)
    position_size > 0 -> exit(stop = avg x 0.98, limit = avg x 1.04);  position_size < 0 -> exit(stop = avg x 1.02, limit = avg x 0.96)

Interpretation choices (Pine rules in SURVEY_README.md)
    * The day counter resets on the first bar of each day: the house day is the broker day (17:00
      America/New_York). It counts accepted signals, including one while already in that side (which
      adds nothing). The bracket is re-sent from position_avg_price every bar from the fill bar's close,
      so it is fixed at the fill: ported as sl_stop 0.02 / tp_stop 0.04 (stated approximation: the source
      acts from the bar after the fill, the house from the fill, as #429494). The band crossing uses the
      current bar's band for both closes, as written. REVERSAL INTENDED. 5 % of equity, capital,
      commission and slippage are sizing and costs. Stop module: portfolio_kwargs {} (driver D4). FREQ =
      "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; 2 % / 4 % bracket from the fill.
    2 generic: PASS, Bollinger re-entries with MACD and volume confirmation, daily signal cap.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: 5 % of equity, capital, commission and slippage stored, not ported.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: used: the bars' volume column (broker tick volume of the cTrader M1 data, summed per bar) against its SMA 20; exchange volume to be compared later (Austin, 2026-10-23).
Session open: broker day (17:00 America/New_York, DST by the zone) for the daily cap; no venue-open rule.
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_482776_bollinger_bounce_macd_volume_daily_cap_2_4pct_1h_reversal"
FAMILY = "bollinger_reversion"  # proposed 2026-10-23 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "sl": [0.02, 0.03],
    "tp": [0.04, 0.06],
}
DEFAULT_PARAMS = {"bb_len": 20, "bb_mult": 2.0, "cap": 5, "sl": 0.02, "tp": 0.04}


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
    n = int(p["bb_len"])
    basis, dev = c.rolling(n).mean(), float(p["bb_mult"]) * c.rolling(n).std(ddof=0)
    upb, lob = basis + dev, basis - dev
    macd = c.ewm(span=12, adjust=False).mean() - c.ewm(span=26, adjust=False).mean()
    sig = macd.ewm(span=9, adjust=False).mean()
    vol_ok = v >= v.rolling(20).mean()
    ls = ((c.shift(1) < lob) & (c > lob) & (macd > sig) & vol_ok).to_numpy()
    ss = ((c.shift(1) > upb) & (c < upb) & (macd < sig) & vol_ok).to_numpy()
    day = np.asarray(broker_day(bars_df.index))
    cap = int(p["cap"])
    m = len(ls)
    le, se = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    count = 0
    for i in range(m):
        if i > 0 and day[i] != day[i - 1]:
            count = 0
        if ls[i] and count < cap:
            le[i], count = True, count + 1
        if ss[i] and count < cap:
            se[i], count = True, count + 1
    ix = bars_df.index
    false = pd.Series(False, index=ix)
    return pd.Series(le, index=ix), false, pd.Series(se, index=ix), false.copy()


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    return {"sl_stop": float(p["sl"]), "tp_stop": float(p["tp"])}


def portfolio_kwargs(**params):
    return {}
