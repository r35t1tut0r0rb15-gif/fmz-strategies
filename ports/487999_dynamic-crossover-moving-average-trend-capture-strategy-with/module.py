"""SMA 10 / 25 crosses on the EMA 250 side, entries from flat, with a tight percentage stop, a percentage trail and an
EMA 250 touch exit, 2-hour bars: flat, above the EMA 250, the SMA 10 crossing above the SMA 25 goes long with a stop
0.07 % under the entry and a 0.07 % trail once 0.21 % in profit; a low touching the EMA 250 closes the trade; shorts
mirror it.
Port of FMZ strategy #487999 "动态交叉移动平均线趋势捕捉策略与风险管理系统-Dynamic-Crossover-Moving-Average-Trend-Capture-Strategy-with-Risk-Management-System" (crypto strat).

FMZ source id: 487999

Source
    https://www.fmz.com/strategy/487999 (PineScript v5, FMZ last modified 2025-03-24 11:59:09).
    Verbatim copy: original_source.md. Read 2026-10-17 (FMZ-C laptop lane).

Original signal (original_source.md lines 213-263), SMA 10 / 25, EMA 250, risk 7 USD, leverage 100
    long = crossover(sma10, sma25) and close > ema250 and position_size == 0 (short mirrored)
    positionSize = 100 x 100 / close;  stopLossDistance = 7 / positionSize = 0.07 % of the close
    entry + exit(stop = close -+ dist, trail_points = 3 x dist, trail_offset = dist)
    position_size > 0 and low <= ema250 -> close long;  position_size < 0 and high >= ema250 -> close short

Interpretation choices (Pine rules in SURVEY_README.md)
    * The stop distance is a fixed fraction of the close (risk / (100 x leverage) = 0.0007): sl_stop 0.0007 of the
      fill (scalar).
    * The trail: price distances in tick arguments read as price distances (#427592): activation 3 x 0.07 % above the
      entry, offset 0.07 %, from the best high (low for shorts): the house trail {"type": "percent", "pct": 0.0007,
      "activate_after": 0.0021, "anchor": "high_low"} (the house offset is a fraction of the best price, the source's
      a fixed price distance of the signal close: equal to within 0.21 %). Mark trailing_stop.
    * The EMA 250 touch is bar-range-checked: an exit signal at the next open (rule 3; #489638), from the position
      held at the bar's start.
    * Entries only from flat: simulate() mirrors the stop and the trail on the bars from the fill bar (an
      approximation of the house minute engine, #430254) so entries and exits follow the position. Opposite entries
      cannot occur.
    * The leveraged quantity is sizing (quoted). Stop module: portfolio_kwargs {} (D4). FREQ = "2h" from the backtest
      header: coarse_bar_stop.

Admission criteria
    1 fits the interface: PASS, bar-close orders; stop and trail from the fill (house trail).
    2 generic: PASS, moving averages and percentages of price.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: the leveraged quantity quoted; the stop and trail ported via stops() and quoted in
      original_sizing.txt.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
Opposite entries cannot occur.

Marks: coarse_bar_stop, trailing_stop
"""
import numpy as np
import pandas as pd

NAME = "fmz_487999_sma_cross_ema250_pct_trail"
FAMILY = "ma_cross"  # proposed 2026-10-17 (FMZ-C laptop lane), user to confirm
FREQ = "2h"  # backtest header period: 2h
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "stop_frac": [0.0007, 0.0021],
    "act_mult": [3.0, 6.0],
}
DEFAULT_PARAMS = {"fast": 10, "slow": 25, "ema_len": 250, "stop_frac": 0.0007, "act_mult": 3.0}


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
    f, s = c.rolling(int(p["fast"])).mean(), c.rolling(int(p["slow"])).mean()
    ema = c.ewm(span=int(p["ema_len"]), adjust=False).mean()
    go_l = ((f > s) & (f.shift(1) <= s.shift(1)) & (c > ema)).to_numpy()
    go_s = ((f < s) & (f.shift(1) >= s.shift(1)) & (c < ema)).to_numpy()
    touch_l = (bars_df["low"] <= ema).to_numpy()
    touch_s = (bars_df["high"] >= ema).to_numpy()
    ov, hv, lv = (bars_df[k].to_numpy(dtype=float) for k in ("open", "high", "low"))
    sf, act = p["stop_frac"], p["act_mult"] * p["stop_frac"]
    m = len(c)
    le, lx, se, sx = (np.zeros(m, dtype=bool) for _ in range(4))
    pos, fill_i, best, level = 0, -1, np.nan, np.nan
    for i in range(m):
        if pos != 0 and i >= fill_i:                     # mirror of the house stop and trail from the fill
            e = ov[fill_i]
            if i == fill_i:
                best, level = e, e * (1 - sf) if pos == 1 else e * (1 + sf)
            if (pos == 1 and lv[i] <= level) or (pos == -1 and hv[i] >= level):
                pos = 0
            elif pos == 1:
                best = max(best, hv[i])
                if best >= e * (1 + act):
                    level = max(level, best * (1 - sf))
            else:
                best = min(best, lv[i])
                if best <= e * (1 - act):
                    level = min(level, best * (1 + sf))
        start = pos
        if pos == 0 and go_l[i]:
            pos, fill_i = 1, i + 1
        elif pos == 0 and go_s[i]:
            pos, fill_i = -1, i + 1
        if start == 1 and touch_l[i]:
            pos = 0
        if start == -1 and touch_s[i]:
            pos = 0
        if pos != start:
            le[i] = pos == 1
            se[i] = pos == -1
            lx[i] = start == 1 and pos == 0
            sx[i] = start == -1 and pos == 0
    idx = bars_df.index
    return tuple(pd.Series(x, index=idx) for x in (le, lx, se, sx))


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    sf = p["stop_frac"]
    return {"sl_stop": sf,
            "trail": {"type": "percent", "pct": sf, "activate_after": p["act_mult"] * sf, "anchor": "high_low"}}


def portfolio_kwargs(**params):
    return {}
