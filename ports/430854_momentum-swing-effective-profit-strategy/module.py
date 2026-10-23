"""Strong-bar momentum entries above the SMA 60, broker days, long only, through the script's own in-position flag: a tight-ranged bar 6 % over the previous close (or a 5 % bar on a 60-bar volume high with the close crossing its EMA 5 ratio's SMA 9 in a rising SMA 50) buys; a close under the EMA 10 closes; a 50 % stop and a 30 % target from the entry.
Port of FMZ strategy #430854 "Momentum Swing Effective Profit Strategy" (Slight Swing Momentum Strategy.).

FMZ source id: 430854

Source
    https://www.fmz.com/strategy/430854 (PineScript v5, FMZ last modified 2023-11-02 15:02:05).
    Verbatim copy: original_source.md. Read 2026-10-23 (FMZ-C).

Original signal (original_source.md lines 129-184), SMA 60; A1 high / close < 1.03, open / low < 1.03, high / close[1] > 1.06; A2 5 % bar; A3 volume over its 60-bar high; XG crossover(close / ema5, sma 9); SMA 50 slope over 4; SL 50 %, TP 30 %
    buySignal = A1 and close > ma60 or A2 and A3 and XG and close > ma60 and weeklySlope;  buySignal and not inPosition -> entry Buy, inPosition := true
    close < ema(10) and inPosition -> close Buy, inPosition := false;  inPosition -> exit(stop = avg x 0.5), exit(limit = avg x 1.3)

Interpretation choices (Pine rules in SURVEY_README.md)
    * "and" binds before "or": either A1 above the SMA 60, or the full A2 / A3 / XG / slope set, as written.
      The flag inPosition is the script's own: after a stop or target fill it stays true until a close
      under the EMA 10 resets it, so no new entry comes before that (as the source). The 50 % stop and 30 %
      target are scalar fractions of the fill. Long only. Stop module: portfolio_kwargs {} (driver D4).
      Stops on 1-day bars: mark coarse_bar_stop. No sizing code. Daily bars are broker days (17:00
      America/New_York), stamped with their first minute. FREQ = "1D" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; percent bracket from the fill.
    2 generic: PASS, strong-bar momentum above a moving average.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: used: the bars' volume column (broker tick volume of the cTrader M1 data, summed per bar) in A3 = crossover(volume, highest(volume, 60)[1]); exchange volume to be compared later (Austin, 2026-10-23).
Session open: broker day (17:00 America/New_York, DST by the zone); no venue-open rule.
Long only.

Marks: coarse_bar_stop
"""
import numpy as np
import pandas as pd

NAME = "fmz_430854_strong_bar_momentum_sma60_volume_high_ema10_exit_long"
FAMILY = "momentum_breakout"  # proposed 2026-10-23 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "ma_len": [60, 100],
    "exit_ema": [10, 20],
}
DEFAULT_PARAMS = {"ma_len": 60, "exit_ema": 10, "sl": 0.5, "tp": 0.3}


def broker_day(index):
    """Broker day of each timestamp: the session ending 17:00 America/New_York, labelled by its
    end date (as worker A's ports). The desktop binds this name to registry_schema.broker_day."""
    ny = index.tz_convert("America/New_York")
    return (ny + pd.Timedelta(hours=7)).normalize().tz_localize(None)


def precompute(raw_1m_df, symbol_key, **params):
    df = raw_1m_df[["open", "high", "low", "close", "volume"]].dropna(subset=["close"])
    if df.index.tz is None:
        raise ValueError("raw_1m_df must have a tz-aware UTC index")
    lab = broker_day(df.index)
    bars = df.groupby(lab).agg({"open": "first", "high": "max", "low": "min", "close": "last", "volume": "sum"})
    first = pd.Series(df.index, index=df.index).groupby(lab).first()
    bars.index = pd.DatetimeIndex(first.loc[bars.index].values)   # each bar stamped with its first minute
    if bars.index.tz is None:
        bars.index = bars.index.tz_localize("UTC")
    return bars


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    o, h, lo, c, v = (bars_df[k] for k in ("open", "high", "low", "close", "volume"))
    ma = c.rolling(int(p["ma_len"])).mean()
    a1 = (h / c < 1.03) & (o / lo < 1.03) & (h / c.shift(1) > 1.06)
    a2 = (c / o > 1.05) | (c / c.shift(1) > 1.05)
    hv = v.rolling(60).max().shift(1)
    a3 = (v > hv) & (v.shift(1) <= hv.shift(1))
    b1 = c / c.ewm(span=5, adjust=False).mean()
    b1s = b1.rolling(9).mean()
    xg = (b1 > b1s) & (b1.shift(1) <= b1s.shift(1))
    wm = c.rolling(50).mean()
    slope = (wm - wm.shift(4)) / 4 > 0
    buy = ((a1 & (c > ma)) | (a2 & a3 & xg & (c > ma) & slope)).to_numpy()
    sell = (c < c.ewm(span=int(p["exit_ema"]), adjust=False).mean()).to_numpy()
    m = len(buy)
    le, lx = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    inpos = False
    for i in range(m):
        if buy[i] and not inpos:
            le[i], inpos = True, True
        if sell[i] and inpos:
            lx[i], inpos = True, False
    ix = bars_df.index
    false = pd.Series(False, index=ix)
    le_s, lx_s = pd.Series(le, index=ix), pd.Series(lx, index=ix)
    return le_s & ~lx_s, lx_s, false, false.copy()


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    return {"sl_stop": float(p["sl"]), "tp_stop": float(p["tp"])}


def portfolio_kwargs(**params):
    return {}
