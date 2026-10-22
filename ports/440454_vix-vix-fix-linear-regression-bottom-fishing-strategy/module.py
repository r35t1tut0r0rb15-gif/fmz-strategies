"""Williams Vix Fix bottoms with a regression filter, 1-hour bars, long only: once the Vix Fix has spiked (above its Bollinger band or 85 % of its 50-bar high) while flat, a positive but falling 22-bar
regression of it goes long; while the regression is positive and rising, a close under the ratcheting close - 5 ATR(22) line closes.
Port of FMZ strategy #440454 "基于Vix修复线性回归的低点捕捉策略Vix-Fix-Linear-Regression-Bottom-Fishing-Strategy" (VixFixLinReg - Strategy).

FMZ source id: 440454

Source
    https://www.fmz.com/strategy/440454 (PineScript v4, FMZ last modified 2024-01-30 16:56:39).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 134-198), VIX fix 22; BB 20 / 2; percentile 50 / 0.85; ATR 22 x 5, initial stop lowest 5; wait for close on; VIX-fix close off
    wvf = (highest(close, 22) - low) / highest(close, 22) x 100;  spike = wvf >= sma(wvf, 20) + 2 sd or wvf >= 0.85 highest(wvf, 50);  state = spike, held at 1 while flat;  val = linreg(wvf, 22, 0)
    long: state 1 and val positive and not rising -> entry Long;  stop = flat ? lowest(low, 5) : max(close - 5 atr(22), stop[1]);  close Long when close < stop and val positive and rising

Interpretation choices (Pine rules in SURVEY_README.md)
    * The exit is a close test sent at the next open (the stop order is used only with "wait for close"
      off). The colours are read as written: lime = positive and not rising, green = positive and
      rising. The flat-state latch keeps any spike since the last exit. Position tests use the held
      position. The date window is dropped. Pine's stdev is the population deviation. Long only. The
      100 % of equity size, capital and commission are sizing and costs. FREQ = "1h" from the backtest
      header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; close-tested ratcheting line.
    2 generic: PASS, Vix Fix, its regression and ATR line.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: percent of equity, capital and commission settings.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
Long only.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_440454_vix_fix_linreg_bottoms_long"
FAMILY = "volatility_spike_reversal"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "atr_mult": [5, 3],
    "pd": [22, 14],
}
DEFAULT_PARAMS = {"atr_mult": 5, "pd": 22, "bbl": 20, "mult": 2.0, "lb": 50, "ph": 0.85, "atr_len": 22, "init_bars": 5}


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


def _atr(bars_df, n):
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    pc = c.shift(1)
    tr = pd.concat([h - lo, (h - pc).abs(), (lo - pc).abs()], axis=1).max(axis=1)
    return _rma(tr, int(n))


def _linreg(y, n):
    """Pine linreg(y, n, 0): the least-squares line over the last n bars, valued at the current bar."""
    g = pd.Series(np.arange(len(y), dtype=float), index=y.index)
    sy = y.rolling(n).sum()
    sgy = (g * y).rolling(n).sum()
    sg = g.rolling(n).sum()
    sgg = (g * g).rolling(n).sum()
    slope = (n * sgy - sg * sy) / (n * sgg - sg * sg)
    icpt = (sy - slope * sg) / n
    return icpt + slope * g


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    lo, c = bars_df["low"], bars_df["close"]
    n = int(p["pd"])
    hc = c.rolling(n).max()
    wvf = (hc - lo) / hc * 100
    bbl = int(p["bbl"])
    upper = wvf.rolling(bbl).mean() + float(p["mult"]) * wvf.rolling(bbl).std(ddof=0)
    spike = ((wvf >= upper) | (wvf >= wvf.rolling(int(p["lb"])).max() * float(p["ph"]))).to_numpy()
    val = _linreg(wvf, n)
    rising = (val > val.shift(1)).to_numpy()
    pos_v = (val > 0).to_numpy()
    lime = pos_v & ~rising
    green = pos_v & rising
    cv = c.to_numpy(dtype=float)
    line = (c - float(p["atr_mult"]) * _atr(bars_df, p["atr_len"])).to_numpy()
    low5 = lo.rolling(int(p["init_bars"])).min().to_numpy()
    m = len(cv)
    le, lx = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    held, state, stop = False, 0, np.nan
    for i in range(m):
        raw = 1 if spike[i] else 0
        state = max(raw, state) if not held else raw
        if held:
            stop = line[i] if np.isnan(stop) else (stop if np.isnan(line[i]) else max(line[i], stop))
        else:
            stop = low5[i]
        nxt = held
        if state == 1 and lime[i] and not held and i + 1 < m:
            le[i], nxt = True, True
        if held and cv[i] < stop and green[i]:
            lx[i], nxt = True, False
        held = nxt
    ix = bars_df.index
    false = pd.Series(False, index=ix)
    return pd.Series(le, index=ix), pd.Series(lx, index=ix), false, false.copy()


def portfolio_kwargs(**params):
    return {}
