"""One-minute bars: the close crossing over the previous 96-bar Donchian high with the Larry Williams large-trade index (25) above 50 and volume above its SMA 30 goes long, the mirror short, only after the close has crossed the channel basis since the last trade; a target twice 1.02 x the entry's distance from the basis at the signal, and a close back through the basis, end each.
Port of FMZ strategy #448079 "Donchian Channel and Larry Williams Large Trade Index Strategy" (Donchian Channel Strategy [DillonGrech]).

FMZ source id: 448079

Source
    https://www.fmz.com/strategy/448079 (PineScript v5, FMZ last modified 2024-04-12 17:27:25).
    Verbatim copy: original_source.md. Read 2026-10-23 (FMZ-C).

Original signal (original_source.md lines 136-319), Donchian 96; LWTI 25 (no smoothing); volume SMA 30; stop and target on, R:R 2
    entry_long = position_size <= 0 and crossover(close, don_upper[1]) and LWTI > 50 and volume > sma(volume, 30) and Trade_Counter[1] == 0;  entry_short mirror
    exit('Exit Long', stop = entry - dist);  exit('Exit Long', limit = entry + 2 x dist)  (dist = |entry - basis at the signal| x 1.02);  close < basis -> close long;  shorts mirrored

Interpretation choices (Pine rules in SURVEY_README.md)
    * Both exits of a side share one id, so the second call (the limit) replaces the stop every bar:
      only the take-profit acts (weird case). The target is a level from the fill price and the basis of
      the signal bar: a fraction of the fill, exact. Trade_Counter is 1 while a position is open and
      resets to 0 when the close crosses the basis while flat, so a new trade needs that reset; the
      signals follow the target for the position state. LWTI = sma(close - nz(close[25]), 25) / ATR 25 x 50
      + 50, so above 50 means the 25-bar change average is positive. The basis close acts only on a
      position the bar's entries leave unchanged. REVERSAL INTENDED (in practice the reset rule keeps
      trades apart). No sizing code. Stop module: portfolio_kwargs {} (driver D4). FREQ = "1min" from the
      backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; basis-distance target from the fill.
    2 generic: PASS, Donchian breakouts with LWTI and volume filters, one trade per basis cross.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: used: the bars' volume column (broker tick volume of the cTrader M1 data) against its SMA 30; exchange volume to be compared later (Austin, 2026-10-23).
Session open: none (24 h).
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_448079_donchian96_breakout_lwti_volume_basis_target_1m"
FAMILY = "volatility_channel_breakout"  # proposed 2026-10-23 (FMZ-C), user to confirm
FREQ = "1min"  # backtest header period: 1m
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "don_length": [96, 48],
    "rr": [2.0, 1.0],
}
DEFAULT_PARAMS = {"don_length": 96, "lwti_per": 25, "vol_len": 30, "rr": 2.0}


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


def _basis(bars_df, p):
    n = int(p["don_length"])
    up, dn = bars_df["high"].rolling(n).max(), bars_df["low"].rolling(n).min()
    return up, dn, (up + dn) / 2


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    o, h, lo, c, v = (bars_df[k] for k in ("open", "high", "low", "close", "volume"))
    up, dn, basis = _basis(bars_df, p)
    k = int(p["lwti_per"])
    pc = c.shift(1)
    tr = pd.concat([h - lo, (h - pc).abs(), (lo - pc).abs()], axis=1).max(axis=1).where(pc.notna())
    lw = (c - c.shift(k).fillna(0.0)).rolling(k).mean() / _rma(tr, k) * 50 + 50
    vol_ok = v > v.rolling(int(p["vol_len"])).mean()
    i1l = (c > up.shift(1)) & (c.shift(1) <= up.shift(2))
    i1s = (c < dn.shift(1)) & (c.shift(1) >= dn.shift(1).shift(1))
    lg = (i1l & (lw > 50) & vol_ok).to_numpy()
    sh = (i1s & ~(lw > 50) & vol_ok).to_numpy()          # red = not above 50
    b1 = basis.shift(1)
    bcross = (((b1 > c) & (b1.shift(1) <= c.shift(1))) | ((b1 < c) & (b1.shift(1) >= c.shift(1)))).to_numpy()
    xl, xs = (c < basis).to_numpy(), (c > basis).to_numpy()
    ov, hv, lv, bv = o.to_numpy(dtype=float), h.to_numpy(dtype=float), lo.to_numpy(dtype=float), basis.to_numpy()
    rr = float(p["rr"])
    m = len(lg)
    le, lx = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    se, sx = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    tgt, tp_px, counter_prev = 0, np.nan, 0
    for i in range(m):
        if i > 0 and le[i - 1]:
            tp_px = ov[i] + rr * abs(ov[i] - bv[i - 1]) * 1.02
        elif i > 0 and se[i - 1]:
            tp_px = ov[i] - rr * abs(ov[i] - bv[i - 1]) * 1.02
        if tgt == 1 and hv[i] >= tp_px:                 # the target ends the trade inside the bar
            tgt = 0
        elif tgt == -1 and lv[i] <= tp_px:
            tgt = 0
        pos = tgt
        if pos != 0:
            counter = 1
        elif bcross[i]:
            counter = 0
        else:
            counter = counter_prev
        new = pos
        if pos <= 0 and lg[i] and counter_prev == 0:
            new = 1
        if pos >= 0 and sh[i] and counter_prev == 0 and new != 1:
            new = -1
        if new == pos:
            if pos == 1 and xl[i]:
                new = 0
            elif pos == -1 and xs[i]:
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
            tgt = new
        counter_prev = counter
    ix = bars_df.index
    return (pd.Series(le, index=ix), pd.Series(lx, index=ix),
            pd.Series(se, index=ix), pd.Series(sx, index=ix))


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    le, lx, se, sx = simulate(bars_df, **params)
    o = bars_df["open"]
    up, dn, basis = _basis(bars_df, p)
    dist = (o - basis.shift(1)).abs() * 1.02 * float(p["rr"]) / o
    filled = le.shift(1, fill_value=False) | se.shift(1, fill_value=False)
    return {"tp_stop": dist.where(filled & (dist > 0))}


def portfolio_kwargs(**params):
    return {}
