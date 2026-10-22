"""SMA 20 / 200 crossings with ADX (10 / 10) over 20 and a "stochastic" crossing, 2-hour bars: the cross up with its stochastic crossing up under 30 goes long, the cross down with it crossing down over 70 goes short, each with a 5-tick trail after 40 ticks of profit; reversing after the first bar.
Port of FMZ strategy #482447 "Multi Indicator Trend Following with Oscillator Alert Strategy" (XAU/USD 5M SMA + Stochastic RSI + ADX Strategy).

FMZ source id: 482447

Source
    https://www.fmz.com/strategy/482447 (PineScript v6, FMZ last modified 2025-02-18 14:54:47).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 91-181), SMA 20 / 200; ADX 10 / 10, 20; stoch(close, 14, 3, 3) and its SMA 3; levels 30 / 70; trail 40 / 5 ticks; re-entry delay 1 bar; qty 1
    k = ta.stoch(close, 14, 3, 3) (high = 14, low = 3 as numbers);  d = sma(k, 3);  long = crossover(sma20, sma200) and adx > 20 and crossover(k, d) and k < 30;  short mirror (k > 70)
    long and short and barssince(flat) > 1 -> close BUY, entry SELL (mirror);  flat and long -> entry BUY;  flat and short -> entry SELL;  exit(trail_points = 40, trail_offset = 5)

Interpretation choices (Pine rules in SURVEY_README.md)
    * ta.stoch is called with the numbers 14 and 3 as its high and low series, so k = 100 (close - 3) /
      (14 - 3), as written: on prices above 3.3 it is always over 30 (no longs) and its crossings are the
      close crossing its 3-bar mean. The reversal needs the position held for more than one bar, so an
      opposite signal on the bar after an entry signal is ignored. The trail of 5 ticks after 40 ticks of
      profit is 0.5 / 4.0 in price at the 0.1 tick: read as the house percent trail 0.5 / 42000 behind the
      best price, active after 4 / 42000 of gain (as #458242; anchor high_low; mark trailing_stop). The
      ADX is Pine's ta.dmi. REVERSAL INTENDED. Stop module: portfolio_kwargs {} (driver D4). Stops on bars
      longer than 1 hour: mark coarse_bar_stop. The fixed qty is sizing. FREQ = "2h" from the backtest
      header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; house percent trail.
    2 generic: PASS, SMA crossings with ADX and an as-written stochastic filter.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: qty 1 stored, not ported.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
REVERSAL INTENDED.

Marks: coarse_bar_stop, trailing_stop
"""
import numpy as np
import pandas as pd

NAME = "fmz_482447_sma20_200_cross_adx20_stoch_numbers_tick_trail_reversal"
FAMILY = "ma_cross"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "2h"  # backtest header period: 2h
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "adx_min": [20, 25],
    "trail_pct": [1.19048e-05, 1.19048e-03],
}
DEFAULT_PARAMS = {"adx_min": 20, "trail_pct": 1.19048e-05, "activate_pct": 9.52381e-05, "adx_length": 10}


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


def _fixnan(x):
    """Pine fixnan: the last non-NaN value, NaN before the first."""
    v = x.to_numpy(dtype=float)
    idx = np.where(~np.isnan(v), np.arange(len(v)), 0)
    idx = np.maximum.accumulate(idx)
    return pd.Series(v[idx], index=x.index)


def _dmi(b, n):
    h, lo, c = b["high"], b["low"], b["close"]
    up, dn = h.diff(), -lo.diff()
    pdm = up.where((up > dn) & (up > 0), 0.0).where(up.notna())
    mdm = dn.where((dn > up) & (dn > 0), 0.0).where(dn.notna())
    pc = c.shift(1)
    tr = pd.concat([h - lo, (h - pc).abs(), (lo - pc).abs()], axis=1).max(axis=1).where(pc.notna())
    trr = _rma(tr, n)
    plus = _fixnan(100 * _rma(pdm, n) / trr)
    minus = _fixnan(100 * _rma(mdm, n) / trr)
    s = plus + minus
    adx = 100 * _rma((plus - minus).abs() / s.where(s != 0, 1.0), n)
    return plus, minus, adx


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    c = bars_df["close"]
    f, s = c.rolling(20).mean(), c.rolling(200).mean()
    adx = _dmi(bars_df, int(p["adx_length"]))[2]
    k = 100 * (c - 3.0) / (14.0 - 3.0)                 # ta.stoch(close, 14, 3, 3), as written
    d = k.rolling(3).mean()
    strong = adx > float(p["adx_min"])
    lc = (f > s) & (f.shift(1) <= s.shift(1)) & strong & (k > d) & (k.shift(1) <= d.shift(1)) & (k < 30)
    sc = (f < s) & (f.shift(1) >= s.shift(1)) & strong & (k < d) & (k.shift(1) >= d.shift(1)) & (k > 70)
    le = lc & ~sc.shift(1, fill_value=False)           # no reversal on the fill bar of the other side
    se = sc & ~lc.shift(1, fill_value=False)
    false = pd.Series(False, index=c.index)
    return le, false, se, false.copy()


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    return {"trail": {"type": "percent", "pct": float(p["trail_pct"]), "anchor": "high_low",
                      "activate_after": float(p["activate_pct"])}}


def portfolio_kwargs(**params):
    return {}
