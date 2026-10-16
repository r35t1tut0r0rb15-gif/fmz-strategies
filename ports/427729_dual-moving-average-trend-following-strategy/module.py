"""PB trend scalper, 3-hour bars: with the EMA 55 band of lows above the RMA 100 band of highs (plus a 3 %
no-trade zone), a dip that closes back above the band's low after closing under its high goes long;
the mirror goes short (only from flat). Positions close when a bar breaks the 170-bar extreme or the
opposite no-trade line, or at a take-profit.
Port of FMZ strategy #427729 "Dual Moving Average Trend Following Strategy" (PB Trend Scalper).

FMZ source id: 427729

Source
    https://www.fmz.com/strategy/427729 (PineScript v5, FMZ last modified 2023-09-24 13:14:08).
    Verbatim copy: original_source.md. Read 2026-10-16 (FMZ-C).

Original signal (original_source.md lines 167-245), MAs 55 / 100, zone 3 %, extremes 170, TP 6.9
    e55h / e55l = ema(high / low, 55); r100h / r100l = rma(high / low, 100)
    zoneL = r100h x 1.03; zoneS = r100l - r100h x 0.03
    short: e55h < r100l and close[2] < e55l and close[1] > e55l and high[1] < e55h and close < e55h
           and e55h < zoneS and no open trade
    long: e55l > r100h and close[2] > e55h and close[1] < e55h and low[1] > e55l and close > e55l
          and e55l > zoneL and at most one open trade
    close long: low < lowest(low, 170)[1] or low < zoneS; close short: high > highest(high, 170)[1] or high > zoneL
    exit(profit = position_avg_price x 6.9) -- TICKS

Interpretation choices (Pine rules in SURVEY_README.md)
    * AS WRITTEN: `profit` is in ticks, so the take-profit distance is avg price x 6.9 x tick size:
      on the source's BTC_USDT (tick 0.1) 69 % of the price. Ported as `tp_pct`, default 69 (as
      written on BTC); 6.9 (the likely intent) is in the grid. Decision owed.
    * A long can open while a short is open (opentrades <= 1): it reverses; a short needs flat.
      The flat test follows the house take-profit too (the loop marks the position closed once a
      bar's high / low reaches the level from the fill price).
    * The closes are exit signals on the bar's range, filled at the next open (market orders).
      An entry and a close of the same side on one bar: the close acts only on an open position.
    * The leveraged quantity is sizing; downtrade never reaches an order.
    * Stop module: portfolio_kwargs {} (driver D4); REVERSAL INTENDED (long over short only).
    * Stops on 3-hour bars: mark coarse_bar_stop. FREQ = "3h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; take-profit fixed at entry.
    2 generic: ADAPT, tick-scaled distance -> percentage.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: the leveraged quantity stored; the take-profit quoted in original_sizing.txt.
    5 ranges declared: GRID below (8 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
REVERSAL INTENDED.

Marks: coarse_bar_stop
"""
import numpy as np
import pandas as pd

NAME = "fmz_427729_pb_trend_scalper"
FAMILY = "ma_pullback"  # proposed 2026-10-16 (FMZ-C), user to confirm
FREQ = "3h"  # backtest header period: 3h
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "tp_pct": [69.0, 6.9],
    "zone": [3.0, 1.5],
    "longma": [100, 200],
}
DEFAULT_PARAMS = {"shortma": 55, "longma": 100, "zone": 3.0, "hh": 170, "ll": 170, "tp_pct": 69.0}


def _resample(raw_1m_df, freq):
    ohlc = raw_1m_df[["open", "high", "low", "close"]]
    bars = ohlc.resample(freq, label="left", closed="left").agg(
        {"open": "first", "high": "max", "low": "min", "close": "last"})
    bars = bars.dropna(how="all")  # an empty period is not a bar; never forward-filled
    if bars.index.tz is None:
        raise ValueError("raw_1m_df must have a tz-aware UTC index")
    return bars


def _rma(x, n):
    """Wilder smoothing as Pine's rma: SMA seed over the first n valid values, then recursive."""
    v = x.to_numpy(dtype=float)
    out = np.full(v.shape, np.nan)
    valid = np.flatnonzero(~np.isnan(v))
    if len(valid) >= n:
        s = valid[0]
        out[s + n - 1] = v[s:s + n].mean()
        for i in range(s + n, len(v)):
            out[i] = (out[i - 1] * (n - 1) + v[i]) / n
    return pd.Series(out, index=x.index)


def precompute(raw_1m_df, symbol_key, **params):
    return _resample(raw_1m_df, FREQ)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    o, h, lo, c = (bars_df[k] for k in ("open", "high", "low", "close"))
    n = int(p["shortma"])
    e_h, e_l = h.ewm(span=n, adjust=False).mean(), lo.ewm(span=n, adjust=False).mean()
    r_h, r_l = _rma(h, int(p["longma"])), _rma(lo, int(p["longma"]))
    z = p["zone"] / 100
    zl, zs = r_h + r_h * z, r_l - r_h * z
    hh, ll = h.rolling(int(p["hh"])).max().shift(1), lo.rolling(int(p["ll"])).min().shift(1)
    c1, c2 = c.shift(1), c.shift(2)
    short_s = ((e_h < r_l) & (c2 < e_l) & (c1 > e_l) & (h.shift(1) < e_h) & (c < e_h) & (e_h < zs)).to_numpy()
    long_s = ((e_l > r_h) & (c2 > e_h) & (c1 < e_h) & (lo.shift(1) > e_l) & (c > e_l) & (e_l > zl)).to_numpy()
    close_l = ((lo < ll) | (lo < zs)).to_numpy()
    close_s = ((h > hh) | (h > zl)).to_numpy()
    ov, hv, lv = o.to_numpy(dtype=float), h.to_numpy(dtype=float), lo.to_numpy(dtype=float)
    tp = p["tp_pct"] / 100
    m = len(ov)
    le, lx, se, sx = (np.zeros(m, dtype=bool) for _ in range(4))
    pos, entry_i = 0, -1
    for i in range(m):
        if pos != 0 and i >= entry_i:                          # house take-profit from the fill price
            lvl = ov[entry_i] * (1 + tp * pos)
            if (pos == 1 and hv[i] >= lvl) or (pos == -1 and lv[i] <= lvl):
                pos = 0
        start = pos
        if short_s[i] and start == 0:
            se[i] = True
            pos, entry_i = -1, i + 1
        if long_s[i] and start != 1:
            le[i] = True
            pos, entry_i = 1, i + 1
        if start == 1 and close_l[i]:
            lx[i] = True
            pos = 0
        if start == -1 and close_s[i] and not le[i]:
            sx[i] = True
            pos = 0
    idx = bars_df.index
    return (pd.Series(le, index=idx), pd.Series(lx, index=idx),
            pd.Series(se, index=idx), pd.Series(sx, index=idx))


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    return {"tp_stop": float(p["tp_pct"]) / 100}


def portfolio_kwargs(**params):
    return {}
