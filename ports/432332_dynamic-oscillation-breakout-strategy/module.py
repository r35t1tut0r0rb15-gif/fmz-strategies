"""Donchian 20 breakouts in the SMA 8 / 32 trend, long only, broker days: a close above the previous 20-bar high with the
SMA 8 above the SMA 32 goes long with a 3 ATR stop from the signal close; the SMA 8 crossing under the SMA 32 closes
it. The stop re-set on every later signal is not emitted.
Port of FMZ strategy #432332 "Dynamic Oscillation Breakout Strategy" (My Strategy (Robrecht99)).

FMZ source id: 432332

Source
    https://www.fmz.com/strategy/432332 (PineScript v5, FMZ last modified 2023-11-16 15:40:25).
    Verbatim copy: original_source.md. Read 2026-10-17 (FMZ-C).

Original signal (original_source.md lines 138-167), SMA 8 / 32, Donchian 20 of the previous bars, ATR 14, stop 3 ATR
    close > highest(high[1], 20) and sma8 > sma32 -> entry long, exit("exit", "long", stop = close - 3 atr, trail_offset = close - 3 atr)
    crossunder(sma8, sma32) and sma32 > sma8 -> close long

Interpretation choices (Pine rules in SURVEY_README.md)
    * The channel excludes the current bar. The stop is 3 ATR from the signal close: sl_atr x ATR /
      close of the signal bar, shifted one bar inside stops() and re-based on the fill. trail_offset
      without trail_points arms no trail.
    * Every later breakout while long re-issues "exit" with a new level (as #432180): a stop that
      moves after entry cannot be expressed by stops(): rule 2, mark trailing_stop_pending; the port
      keeps the first signal's level for the trade.
    * Long only; Opposite entries cannot occur. The port's state machine follows the house stop on
      bars. Daily bars are broker days (17:00 America/New_York), stamped with their first minute;
      stops on daily bars: mark coarse_bar_stop. Stop module: portfolio_kwargs {} (driver D4). FREQ =
      "1D" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; stop fixed at entry (the re-set pending).
    2 generic: PASS, ATR stop, channel and SMA rules.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: the margin settings stored in original_sizing.txt.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: broker day (17:00 America/New_York, DST by the zone); no venue-open rule.
Long only. Opposite entries cannot occur.

Marks: trailing_stop_pending, coarse_bar_stop
"""
import numpy as np
import pandas as pd

NAME = "fmz_432332_donchian_sma_trend_long"
FAMILY = "donchian_breakout"  # proposed 2026-10-17 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "channel": [20, 55],
    "sl_atr": [3.0, 1.5],
}
DEFAULT_PARAMS = {"fast": 8, "slow": 32, "channel": 20, "atr_len": 14, "sl_atr": 3.0}


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


def _run(bars_df, p):
    o, h, lo, c = (bars_df[k] for k in ("open", "high", "low", "close"))
    f = c.rolling(int(p["fast"])).mean()
    s = c.rolling(int(p["slow"])).mean()
    h1 = h.shift(1).rolling(int(p["channel"])).max()
    el = ((c > h1) & (f > s)).to_numpy()
    xl = ((f < s) & (f.shift(1) >= s.shift(1))).to_numpy()
    c1 = c.shift(1)
    tr = pd.concat([h - lo, (h - c1).abs(), (lo - c1).abs()], axis=1).max(axis=1)
    af = (tr.ewm(alpha=1 / int(p["atr_len"]), adjust=False).mean() / c).to_numpy()
    ov, lv = o.to_numpy(dtype=float), lo.to_numpy(dtype=float)
    k = float(p["sl_atr"])
    m = len(ov)
    tgt = np.zeros(m, dtype=np.int8)
    ent = np.zeros(m, dtype=np.int8)
    sl_arr = np.full(m, np.nan)
    pos, e_i, sl = 0, -1, 0.0
    for i in range(m):
        if pos == 1 and i >= e_i and lv[i] <= ov[e_i] * (1 - sl):   # house stop from the fill price
            pos = 0
        start = pos
        if el[i] and not np.isnan(af[i]) and start == 0:
            pos, e_i, sl = 1, i + 1, af[i] * k
            sl_arr[i] = sl
            ent[i] = 1
        if xl[i] and start == 1:
            pos = 0
        tgt[i] = pos
    return tgt, ent, sl_arr


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    tgt, ent, _ = _run(bars_df, p)
    prev = np.concatenate(([0], tgt[:-1]))
    le = ent == 1
    lx = (prev == 1) & (tgt == 0)
    false = np.zeros(len(tgt), dtype=bool)
    return tuple(pd.Series(a, index=bars_df.index) for a in (le, lx, false, false.copy()))


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    _, _, sl_arr = _run(bars_df, p)
    return {"sl_stop": pd.Series(sl_arr, index=bars_df.index).shift(1)}


def portfolio_kwargs(**params):
    return {}
