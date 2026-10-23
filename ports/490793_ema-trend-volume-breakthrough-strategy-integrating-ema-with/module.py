"""4-day bars (blocks of four broker days): a green bar above the EMA 50 on volume over 2 x its EMA 20 goes long, a red bar below it on the same spike goes short; the trade closes on the 4th bar after the last signal bar, at the next open; reversing.
Port of FMZ strategy #490793 "趋势量能突破策略整合EMA与成交量异常监测系统-Trend-Volume-Breakthrough-Strategy-Integrating-EMA-with-Volume-Anomaly-Detection-System" (AI Volume Strategy).

FMZ source id: 490793

Source
    https://www.fmz.com/strategy/490793 (PineScript v6, FMZ last modified 2025-04-16 15:16:18).
    Verbatim copy: original_source.md. Read 2026-10-23 (FMZ-C).

Original signal (original_source.md lines 151-210), volume EMA 20 x 2; EMA 50 trend; candle colour; exit after 5 bars counted from the last signal
    buySignal = volume > ema(volume, 20) x 2 and close > ema50 and close > open -> entry BUY, barsSinceEntry := 0;  sellSignal mirrored -> entry SELL, barsSinceEntry := 0
    barsSinceEntry += 1 every bar;  barsSinceEntry >= 5 -> close BUY and SELL

Interpretation choices (Pine rules in SURVEY_README.md)
    * The counter restarts on every signal bar, including repeats while in the trade (which add nothing),
      and counts that bar as 1, so the close is sent on the 4th bar after the last signal and fills at the
      next open. An opposite signal reverses. The 4-day bars are blocks of four broker days counted from
      1970-01-01, each stamped with its first minute (the header period 4d). REVERSAL INTENDED. No sizing
      code. FREQ = "4D" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; a bar-count exit in the signals.
    2 generic: PASS, volume-spike candles in the EMA 50 trend with a time exit.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: used: the bars' volume column (broker tick volume of the cTrader M1 data, summed per 4-day block) against 2 x its EMA 20; exchange volume to be compared later (Austin, 2026-10-23).
Session open: blocks of 4 broker days (17:00 America/New_York, DST by the zone); no venue-open rule.
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_490793_volume_spike_candle_ema50_5bar_exit_4d_reversal"
FAMILY = "volume_breakout"  # proposed 2026-10-23 (FMZ-C), user to confirm
FREQ = "4D"  # backtest header period: 4d (blocks of 4 broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "exit_bars": [5, 3],
    "vol_mult": [2.0, 1.5],
}
DEFAULT_PARAMS = {"exit_bars": 5, "vol_mult": 2.0}


def broker_day(index):
    """Broker day of each timestamp: the session ending 17:00 America/New_York, labelled by its
    end date (as worker A's ports). The desktop binds this name to registry_schema.broker_day."""
    ny = index.tz_convert("America/New_York")
    return (ny + pd.Timedelta(hours=7)).normalize().tz_localize(None)


def _multiday(raw_1m_df, days):
    """Blocks of `days` broker days counted from 1970-01-01, each stamped with its first minute."""
    df = raw_1m_df[["open", "high", "low", "close", "volume"]].dropna(subset=["close"])
    if df.index.tz is None:
        raise ValueError("raw_1m_df must have a tz-aware UTC index")
    key = np.asarray((broker_day(df.index) - pd.Timestamp("1970-01-01")).days // days)
    bars = df.groupby(key).agg({"open": "first", "high": "max", "low": "min", "close": "last", "volume": "sum"})
    first = pd.Series(df.index, index=df.index).groupby(key).first()
    bars.index = pd.DatetimeIndex(first.loc[bars.index].values)
    if bars.index.tz is None:
        bars.index = bars.index.tz_localize("UTC")
    return bars


def precompute(raw_1m_df, symbol_key, **params):
    return _multiday(raw_1m_df, 4)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    o, c, v = bars_df["open"], bars_df["close"], bars_df["volume"]
    spike = v > v.ewm(span=20, adjust=False).mean() * float(p["vol_mult"])
    ema = c.ewm(span=50, adjust=False).mean()
    buy = (spike & (c > ema) & (c > o)).to_numpy()
    sell = (spike & (c < ema) & (c < o)).to_numpy()
    nx = int(p["exit_bars"])
    m = len(buy)
    le, lx = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    se, sx = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    pos, cnt = 0, 0
    for i in range(m):
        new = pos
        if buy[i]:
            new, cnt = 1, 0
        if sell[i]:
            new, cnt = -1, 0
        cnt += 1
        if new == pos and pos != 0 and cnt >= nx:
            new = 0
        if new != pos and i + 1 < m:
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
