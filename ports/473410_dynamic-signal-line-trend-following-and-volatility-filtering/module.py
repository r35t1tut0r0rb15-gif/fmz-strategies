"""Discontinued-signal-line trend entries, hourly bars, entries only from flat: with three bars opening and closing over the DSL upper line (an SMA 34 kept from closes over the 34-bar high of 30 bars ago), the band over the lower line, and a DSL-Beluga oscillator (RSI 10) crossing up through its lower level under 55, it buys with the band as stop and a 1.5 R target; the mirror sells.
Port of FMZ strategy #473410 "Dynamic Signal Line Trend Following and Volatility Filtering Strategy" (DSL Strategy [DailyPanda]).

FMZ source id: 473410

Source
    https://www.fmz.com/strategy/473410 (PineScript v5, FMZ last modified 2024-11-29 17:02:33).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 96-305), DSL length 34, offset 30, band width 1 x ATR 200; Beluga RSI 10, Fast mode; risk-reward 1.5; daily goal off
    dsl_up := close > highest(high, 34)[30] ? sma(close, 34) : nz(dsl_up[1]);  dsl_dn mirror on lowest(low, 34)[30];  band up = dsl_up - atr200, band dn = dsl_dn + atr200;  osc = zlema((lvlu + lvld) / 2, 10) of RSI-10 DSL lines;  long: up1 > dsl_dn and 3 bars over dsl_up and crossover(osc, level_dn) and osc < 55 and flat -> stop = up1, target = close + 1.5 (close - up1), entry Long + exit;  short mirror

Interpretation choices (Pine rules in SURVEY_README.md)
    * The kept DSL lines start at 0 (nz), as written. dsl_lines: up := src > sma(src, n) ? up[1] + 2 / n
      x (src - up[1]) : up[1] (Fast mode 2), from 0; the ZLEMA lag is floor((10 - 1) / 2) = 4. The
      daily-goal block reads strategy.equity but is off by default, so it feeds nothing. The bracket is
      sent once, on the signal bar; entries only from flat: a loop follows each trade's bracket on the
      bar's high / low so the flat gate lines up (as 449508), and the levels are sent as fractions of the
      fill open (a level at or through it is marketable and closed one bar late). A bar with both
      setups sends the short last, which wins (#437773). Opposite entries cannot occur. Stop module:
      portfolio_kwargs {} (driver D4). Costs not ported. FREQ = "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; signal-bar bracket as fractions of the fill.
    2 generic: PASS, DSL trend lines with an oscillator trigger and an R-multiple bracket.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: slippage stored, not ported; daily goal off.
    5 ranges declared: GRID below (8 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
Opposite entries cannot occur (entries only from flat).

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_473410_dsl_lines_beluga_osc_band_stop_rr_from_flat"
FAMILY = "trend_confluence"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "length": [34, 50],
    "offset": [30, 15],
    "risk_reward": [1.5, 2.0],
}
DEFAULT_PARAMS = {"length": 34, "offset": 30, "risk_reward": 1.5, "width": 1.0, "beluga": 10, "mode": 2}


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


def _rsi(c, n):
    d = c.diff()
    up, dn = _rma(d.clip(lower=0), n), _rma((-d).clip(lower=0), n)
    return 100 - 100 / (1 + up / dn)


def _atr(bars_df, n):
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    pc = c.shift(1)
    tr = pd.concat([h - lo, (h - pc).abs(), (lo - pc).abs()], axis=1).max(axis=1)
    return _rma(tr, int(n))


def _kept(val, hit):
    """var-style line: val on bars where hit holds, else the previous value (nz seed 0)."""
    v, k = val.to_numpy(dtype=float), hit.to_numpy()
    out = np.zeros(len(v))
    cur = 0.0
    for i in range(len(v)):
        if k[i]:
            cur = v[i]
        out[i] = cur
    return pd.Series(out, index=val.index)


def _dsl_lines(src, n, mode):
    s = src.to_numpy(dtype=float)
    ma = src.rolling(n).mean().to_numpy(dtype=float)
    up, dn = np.zeros(len(s)), np.zeros(len(s))
    u = d = 0.0
    for i in range(len(s)):
        if s[i] > ma[i]:
            u = u + mode / n * (s[i] - u)
        if s[i] < ma[i]:
            d = d + mode / n * (s[i] - d)
        up[i], dn[i] = u, d
    return pd.Series(up, index=src.index), pd.Series(dn, index=src.index)


def _run(bars_df, p):
    o, h, lo, c = (bars_df[k] for k in ("open", "high", "low", "close"))
    n, off = int(p["length"]), int(p["offset"])
    sma = c.rolling(n).mean()
    dsl_up = _kept(sma, c > h.rolling(n).max().shift(off))
    dsl_dn = _kept(sma, c < lo.rolling(n).min().shift(off))
    atr = _atr(bars_df, 200) * float(p["width"])
    up1, dn1 = dsl_up - atr, dsl_dn + atr
    lvlu, lvld = _dsl_lines(_rsi(c, 10), int(p["beluga"]), int(p["mode"]))
    x = (lvlu + lvld) / 2
    osc = (2 * x - x.shift(4)).ewm(span=10, adjust=False).mean()
    lev_up, lev_dn = _dsl_lines(osc, 10, int(p["mode"]))
    up_sig = (osc > lev_dn) & (osc.shift(1) <= lev_dn.shift(1)) & (osc < 55)
    dn_sig = (osc < lev_up) & (osc.shift(1) >= lev_up.shift(1)) & (osc > 50)
    above = (o > dsl_up) & (c > dsl_up)
    below = (o < dn1) & (c < dn1)
    lc = (up1.notna() & (up1 > dsl_dn) & above & above.shift(1, fill_value=False)
          & above.shift(2, fill_value=False) & up_sig & (c - up1 > 0)).to_numpy()
    sc = (dn1.notna() & (dsl_dn < up1) & below & below.shift(1, fill_value=False)
          & below.shift(2, fill_value=False) & dn_sig & (dn1 - c > 0)).to_numpy()
    ov, hv, lv, cv = (z.to_numpy(dtype=float) for z in (o, h, lo, c))
    u1, d1 = up1.to_numpy(dtype=float), dn1.to_numpy(dtype=float)
    rr = float(p["risk_reward"])
    m = len(ov)
    le, lx = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    se, sx = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    sl_sent, tp_sent, side = np.full(m, np.nan), np.full(m, np.nan), np.zeros(m)
    pos, pend, sl, tp, sl_n, tp_n = 0, 0, np.nan, np.nan, np.nan, np.nan
    for i in range(m):
        if pend in (1, -1):
            pos, pend, sl, tp = pend, 0, sl_n, tp_n
            through = (sl >= ov[i] or tp <= ov[i]) if pos == 1 else (sl <= ov[i] or tp >= ov[i])
            if through:                          # a level through the fill: closed at the next open
                if pos == 1:
                    lx[i] = True
                else:
                    sx[i] = True
                pend, sl, tp = 2, np.nan, np.nan
        elif pend == 2:
            pos, pend, sl, tp = 0, 0, np.nan, np.nan
        if pos == 1 and (lv[i] <= sl or hv[i] >= tp):
            pos, sl, tp = 0, np.nan, np.nan      # the bracket fills inside this bar
        elif pos == -1 and (hv[i] >= sl or lv[i] <= tp):
            pos, sl, tp = 0, np.nan, np.nan
        if pend != 0 or pos != 0:
            continue
        if sc[i]:                                # the short block runs last and wins a bar with both
            sl_n, tp_n = d1[i], cv[i] - (d1[i] - cv[i]) * rr
            se[i], pend, sl_sent[i], tp_sent[i], side[i] = True, -1, sl_n, tp_n, -1
        elif lc[i]:
            sl_n, tp_n = u1[i], cv[i] + (cv[i] - u1[i]) * rr
            le[i], pend, sl_sent[i], tp_sent[i], side[i] = True, 1, sl_n, tp_n, 1
    ix = bars_df.index
    return [pd.Series(z, index=ix) for z in (le, lx, se, sx, sl_sent, tp_sent, side)]


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    return tuple(_run(bars_df, p)[:4])


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    sl_l, tp_l, sd = _run(bars_df, p)[4:]
    o = bars_df["open"]
    sl_l, tp_l, sd = sl_l.shift(1), tp_l.shift(1), sd.shift(1)    # the signal bar's levels, read at the fill
    sl_f = (1 - sl_l / o).where(sd > 0, sl_l / o - 1)
    tp_f = (tp_l / o - 1).where(sd > 0, 1 - tp_l / o)
    return {"sl_stop": sl_f.where(sl_f > 0), "tp_stop": tp_f.where(tp_f > 0)}


def portfolio_kwargs(**params):
    return {}
