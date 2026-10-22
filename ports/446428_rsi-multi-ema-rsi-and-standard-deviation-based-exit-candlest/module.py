"""Breakouts of the previous 4 bars' range on the side of the EMA 55, daily bars, with the script's state flags: from no flagged trade, a close above the prior 4-bar high and the EMA 55 goes long, below the
prior 4-bar low and the EMA goes short; a flagged long closes on a close under the upper exit band (SMA 12 + 0.5 sd) or the EMA 12, a flagged short mirrored.
Port of FMZ strategy #446428 "基于多重移动平均线RSI-和标准差出场的蜡烛线高度突破交易策略Multi-EMA-RSI-and-Standard-Deviation-Based-Exit-Candlestick-Height-Breakout-Trading-Strategy" (CHB Single Signal (Candle Height Breakout with Configurable Exit)).

FMZ source id: 446428

Source
    https://www.fmz.com/strategy/446428 (PineScript v5, FMZ last modified 2024-03-28 16:13:45).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 122-198), EMA filter 55 on; candle count 4; exit EMA / SMA 12, std-dev multiplier 0.5; EMAs 6 / 8 / 12 / 55 / 100 / 150 / 200 plot only
    longEntry = not inLong and not inShort and close > highest(high[1], 4) and close > ema55 -> entry Buy, inLong;  shortEntry mirrored -> entry Sell, inShort
    exitLong = inLong and (close < sma12 + 0.5 sd12 or close < ema12) -> close Buy, inLong = false;  exitShort = inShort and (close > sma12 - 0.5 sd12 or close > ema12) -> close Sell

Interpretation choices (Pine rules in SURVEY_README.md)
    * The flags are set at the entry call, before the exit test of the same bar, so an exit test true
      on the entry bar clears the flag while the entry still fills (strategy.close finds no position
      yet): the position then stays open with no flag, and only a later opposite entry ends it, as
      written. The port runs the flags and the position side by side in the script's order. Pine's
      stdev is the population deviation. REVERSAL INTENDED. No sizing code. FREQ = "1D" from the
      backtest header (broker days).

Admission criteria
    1 fits the interface: PASS, bar-close orders; the prior bars' range excludes the current bar.
    2 generic: PASS, range breakouts with an EMA filter and band / EMA exits.
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

NAME = "fmz_446428_prior4_range_break_ema55_flag_exits_reversal"
FAMILY = "breakout"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "candle_count": [4, 3],
    "exit_len": [12, 20],
}
DEFAULT_PARAMS = {"candle_count": 4, "exit_len": 12, "ema_filter": 55, "sd_mult": 0.5}


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
    k = int(p["candle_count"])
    hh = h.shift(1).rolling(k).max()
    ll = lo.shift(1).rolling(k).min()
    ef = c.ewm(span=int(p["ema_filter"]), adjust=False).mean()
    n = int(p["exit_len"])
    ee = c.ewm(span=n, adjust=False).mean()
    sma, sd = c.rolling(n).mean(), c.rolling(n).std(ddof=0)
    up_b, lo_b = sma + float(p["sd_mult"]) * sd, sma - float(p["sd_mult"]) * sd
    with np.errstate(invalid="ignore"):
        brk_l = ((c > hh) & (c > ef)).to_numpy()
        brk_s = ((c < ll) & (c < ef)).to_numpy()
        xl = ((c < up_b) | (c < ee)).to_numpy()
        xs = ((c > lo_b) | (c > ee)).to_numpy()
    m = len(c)
    le, lx = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    se, sx = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    pos, in_l, in_s = 0, False, False
    for i in range(m):
        new = pos
        free = not in_l and not in_s
        if free and brk_l[i]:
            if new != 1:
                le[i], new = True, 1
            in_l, in_s = True, False
        if free and brk_s[i]:
            if new != -1:
                se[i], le[i], new = True, False, -1
            in_l, in_s = False, True
        if in_l and xl[i]:
            if pos == 1 and new == 1:               # strategy.close acts only on a held long
                lx[i], new = True, 0
            in_l = False
        if in_s and xs[i]:
            if pos == -1 and new == -1:
                sx[i], new = True, 0
            in_s = False
        pos = new
    ix = bars_df.index
    return (pd.Series(le, index=ix), pd.Series(lx, index=ix),
            pd.Series(se, index=ix), pd.Series(sx, index=ix))


def portfolio_kwargs(**params):
    return {}
