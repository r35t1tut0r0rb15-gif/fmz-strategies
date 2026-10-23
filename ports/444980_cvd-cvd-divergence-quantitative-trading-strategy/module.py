"""Broker days: a regular or hidden bullish divergence between the low and the cumulative volume delta at a confirmed CVD pivot low (7 / 3, the previous pivot 5 .. 60 bars back) goes long; the bearish mirror at pivot highs goes short; a 5 % stop and a 10 % target from the entry; reversing.
Port of FMZ strategy #444980 "CVD背离量化交易策略CVD-Divergence-Quantitative-Trading-Strategy" (CVD Divergence Strategy.1.mm (mmattman)).

FMZ source id: 444980

Source
    https://www.fmz.com/strategy/444980 (PineScript v5, FMZ last modified 2024-03-15 16:47:47).
    Verbatim copy: original_source.md. Read 2026-10-23 (FMZ-C).

Original signal (original_source.md lines 119-374), pivots 7 / 3 on the CVD; range 5 .. 60; stop 5 %, target 10 %
    delta = bullPower / (bullPower + bearPower) x volume - bearPower / (...) x volume;  cvd = cum(delta);  plFound = pivotlow(cvd, 7, 3) exists
    le = (low[3] < previous pivot low[3] and cvd[3] > previous pivot cvd[3]) or (low[3] > ... and cvd[3] < ...) at plFound, previous pivot 5 .. 60 bars back -> entry Long;  se mirror -> entry Short

Interpretation choices (Pine rules in SURVEY_README.md)
    * Bull / bear power are Vadim Gimelfarb's nested range rules, as written; they split each bar's
      volume. A divergence compares the new pivot (3 bars back) with the previous one (valuewhen(..., 1));
      _inRange is the bars since the previous bar's pivot flag. The close calls fire with the opposite
      entry and act only on a position the entry leaves unchanged. The stop and target are levels from
      the average (fill) price: fixed fractions of the fill. REVERSAL INTENDED. No sizing code. Stop module:
      portfolio_kwargs {} (driver D4). Stops on 1-day bars: mark coarse_bar_stop. Daily bars are broker
      days (17:00 America/New_York), stamped with their first minute. FREQ = "1D" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; fixed 5 % / 10 % bracket from the fill.
    2 generic: PASS, price / cumulative-volume-delta pivot divergences.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: used: the bars' volume column (broker tick volume of the cTrader M1 data, summed per bar) split into bull / bear volume for the cumulative delta; exchange volume to be compared later (Austin, 2026-10-23).
Session open: broker day (17:00 America/New_York, DST by the zone); no venue-open rule.
REVERSAL INTENDED.

Marks: coarse_bar_stop
"""
import numpy as np
import pandas as pd

NAME = "fmz_444980_cvd_pivot_divergence_pct_bracket_reversal"
FAMILY = "volume_flow"  # proposed 2026-10-23 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "lb_left": [7, 5],
    "lb_right": [3, 2],
}
DEFAULT_PARAMS = {"lb_left": 7, "lb_right": 3, "range_upper": 60, "range_lower": 5, "sl": 0.05, "tp": 0.10}


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


def _powers(o, h, lo, c):
    c1 = c.shift(1)
    mx = np.maximum
    i1 = np.where(c1 < o, mx(h - c1, c - lo), mx(h - o, c - lo))
    i2 = np.where(c1 > o, h - lo, mx(o - c1, h - lo))
    i3 = np.where(c1 < o, mx(h - c1, c - lo), h - o)
    i4 = np.where(c1 > o, h - lo, mx(o - c1, h - lo))
    i5 = np.where(c1 < o, mx(o - c1, h - lo), h - lo)
    i6 = np.where(c1 > o, mx(h - o, c - lo), i5)
    i7 = np.where(h - c < c - lo, i4, i6)
    i8 = np.where(h - c > c - lo, i3, i7)
    i9 = np.where(c > o, i2, i8)
    bull = np.where(c < o, i1, i9)
    j10 = np.where(c1 > o, mx(c1 - o, h - lo), h - lo)
    j11 = np.where(c1 > o, mx(c1 - lo, h - c), mx(o - lo, h - c))
    j12 = np.where(c1 > o, mx(c1 - o, h - lo), h - lo)
    j13 = np.where(c1 > o, mx(c1 - lo, h - c), o - lo)
    j14 = np.where(c1 < o, mx(o - lo, h - c), h - lo)
    j15 = np.where(c1 > o, mx(c1 - o, h - lo), j14)
    j16 = np.where(h - c < c - lo, j13, j15)
    j17 = np.where(h - c > c - lo, j12, j16)
    j18 = np.where(c > o, j11, j17)
    bear = np.where(c < o, j10, j18)
    return bull, bear


def _pivot_hit(x, side, left, right):
    """pivothigh / pivotlow(x, left, right) found on this bar (strict), and the pivot value x[right]."""
    s = x if side > 0 else -x
    centre = s.shift(right)
    lft = s.shift(right + 1).rolling(left).max()
    rgt = s.rolling(right).max()
    return ((centre > lft) & (centre > rgt)).to_numpy(), x.shift(right).to_numpy(dtype=float)


def _divs(found, osc_r, price_r, low_side, rl, ru):
    m = len(found)
    reg, hid = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    prev_o = prev_p = np.nan
    last_flag = -1                                       # last bar on which found[1] was true
    for i in range(m):
        if i > 0 and found[i - 1]:
            last_flag = i
        bars = i - last_flag if last_flag >= 0 else np.nan
        in_rng = (not np.isnan(bars)) and rl <= bars <= ru
        if found[i]:
            if not np.isnan(prev_o) and in_rng:
                if low_side:
                    reg[i] = price_r[i] < prev_p and osc_r[i] > prev_o
                    hid[i] = price_r[i] > prev_p and osc_r[i] < prev_o
                else:
                    reg[i] = price_r[i] > prev_p and osc_r[i] < prev_o
                    hid[i] = price_r[i] < prev_p and osc_r[i] > prev_o
            prev_o, prev_p = osc_r[i], price_r[i]
    return reg | hid


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    o, h, lo, c, v = (bars_df[k] for k in ("open", "high", "low", "close", "volume"))
    bull, bear = _powers(o, h, lo, c)
    tot = bull + bear
    with np.errstate(invalid="ignore", divide="ignore"):
        delta = np.where(tot != 0, (bull - bear) / tot, np.nan) * v.to_numpy(dtype=float)
    cvd = pd.Series(np.nan_to_num(delta), index=c.index).cumsum()
    L, R = int(p["lb_left"]), int(p["lb_right"])
    pl, _ = _pivot_hit(cvd, -1, L, R)
    ph, _ = _pivot_hit(cvd, 1, L, R)
    osc_r = cvd.shift(R).to_numpy(dtype=float)
    rl, ru = int(p["range_lower"]), int(p["range_upper"])
    le = _divs(pl, osc_r, lo.shift(R).to_numpy(dtype=float), True, rl, ru)
    se = _divs(ph, osc_r, h.shift(R).to_numpy(dtype=float), False, rl, ru)
    ix = bars_df.index
    false = pd.Series(False, index=ix)
    return pd.Series(le & ~se, index=ix), false, pd.Series(se, index=ix), false.copy()


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    return {"sl_stop": float(p["sl"]), "tp_stop": float(p["tp"])}


def portfolio_kwargs(**params):
    return {}
