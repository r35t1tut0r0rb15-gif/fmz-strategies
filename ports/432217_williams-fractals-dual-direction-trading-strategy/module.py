"""Williams fractals in an EMA 20 / 50 / 100 trend, from flat, 1-hour bars: a confirmed down fractal (2 bars each side)
with the EMA 20 above the EMAs 50 and 100, the low two bars back above the EMA 100 and the RSI 14 rising over two bars
goes long; the mirror (up fractal) goes short; a 0.5 % target and a 3.1 % stop from the fill.
Port of FMZ strategy #432217 "Williams Fractals Dual Direction Trading Strategy" (Williams Fractals Strategy).

FMZ source id: 432217

Source
    https://www.fmz.com/strategy/432217 (PineScript v4, FMZ last modified 2023-11-15 16:22:07).
    Verbatim copy: original_source.md. Read 2026-10-17 (FMZ-C).

Original signal (original_source.md lines 204-360), fractal periods 2, EMA 20 / 50 / 100, RSI 14, TP 0.5 %, SL 3.1 %
    downFractal: low[n] below the n lows after it and below the n lows before it (with up to 4 equal lows allowed), n = 2
    ema20 > ema50 and ema20 > ema100 and downFractal and low[2] > ema100 and rsi[2] < rsi and opentrades == 0 -> entry long
    ema20 < ema50 and ema20 < ema100 and upFractal and high[2] < ema100 and rsi[2] > rsi and opentrades == 0 -> entry short
    in position: exit(limit = avg price x (1 +- 0.5 %), stop = avg price x (1 -+ 3.1 %))

Interpretation choices (Pine rules in SURVEY_README.md)
    * The fractal is the bar n = 2 bars back, confirmed at the current bar (only past bars are read);
      its frontier rules are coded as in the source's loops. The RSI is the source's own (Wilder, 100
      when there is no down move, 0 when there is no up move).
    * Entries only from flat (opentrades == 0): the port's state machine follows the house bracket on
      bars, and an entry may follow a bracket exit in the same bar, so Opposite entries cannot occur.
      The bracket is a fixed fraction of the fill by side; Pine places it from the fill bar's close,
      the house bracket is live on the fill bar too (stated). inDateRange is always true.
    * Stop module: portfolio_kwargs {} (driver D4). FREQ = "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; bracket fixed at entry.
    2 generic: PASS, fractals, EMA order, RSI turn and percentage exits of the fill.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: 1000 USD cash per trade stored in original_sizing.txt.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: DG432217 (2 members, best partner #432792, Jaccard 0.944); ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
Opposite entries cannot occur.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_432217_williams_fractal_ema_trend"
FAMILY = "pivot_reversal"  # proposed 2026-10-17 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "tp_pct": [0.5, 1.5],
    "sl_pct": [3.1, 1.5],
}
DEFAULT_PARAMS = {"n": 2, "ema_a": 20, "ema_b": 50, "ema_c": 100, "rsi_len": 14, "tp_pct": 0.5, "sl_pct": 3.1}


def _resample(raw_1m_df, freq):
    ohlc = raw_1m_df[["open", "high", "low", "close"]]
    bars = ohlc.resample(freq, label="left", closed="left").agg(
        {"open": "first", "high": "max", "low": "min", "close": "last"})
    bars = bars.dropna(how="all")  # an empty period is not a bar; never forward-filled
    if bars.index.tz is None:
        raise ValueError("raw_1m_df must have a tz-aware UTC index")
    return bars


def _fractal(x, n, up):
    """The source's fractal loops: up=True for an up fractal on highs, False for a down fractal on lows."""
    lt = (lambda a, b: a < b) if up else (lambda a, b: a > b)       # strictly beyond
    le = (lambda a, b: a <= b) if up else (lambda a, b: a >= b)     # equal allowed
    c = x.shift(n)
    front = pd.Series(True, index=x.index)
    f = [pd.Series(True, index=x.index) for _ in range(5)]
    for i in range(1, n + 1):
        front &= lt(x.shift(n - i), c)
        f[0] &= lt(x.shift(n + i), c)
        for k in range(1, 5):
            eq = pd.Series(True, index=x.index)
            for j in range(1, k + 1):
                eq &= le(x.shift(n + j), c)
            f[k] &= eq & lt(x.shift(n + i + k), c)
    return front & (f[0] | f[1] | f[2] | f[3] | f[4])


def _rsi(x, n):
    d = x.diff()
    up = d.clip(lower=0).ewm(alpha=1 / n, adjust=False).mean()
    dn = (-d.clip(upper=0)).ewm(alpha=1 / n, adjust=False).mean()
    r = 100 - 100 / (1 + up / dn)
    return r.where(dn != 0, 100.0).where(~((up == 0) & (dn != 0)), 0.0)


def _run(bars_df, p):
    o, h, lo, c = (bars_df[k] for k in ("open", "high", "low", "close"))
    n = int(p["n"])
    ea, eb, ec = (c.ewm(span=int(p[k]), adjust=False).mean() for k in ("ema_a", "ema_b", "ema_c"))
    r = _rsi(c, int(p["rsi_len"]))
    upf, dnf = _fractal(h, n, True), _fractal(lo, n, False)
    el = ((ea > eb) & (ea > ec) & dnf & (lo.shift(2) > ec) & (r.shift(2) < r)).to_numpy()
    es = ((ea < eb) & (ea < ec) & upf & (h.shift(2) < ec) & (r.shift(2) > r)).to_numpy()
    ov, hv, lv = o.to_numpy(dtype=float), h.to_numpy(dtype=float), lo.to_numpy(dtype=float)
    tp, sl = float(p["tp_pct"]) / 100, float(p["sl_pct"]) / 100
    m = len(ov)
    tgt = np.zeros(m, dtype=np.int8)
    ent = np.zeros(m, dtype=np.int8)
    pos, e_i = 0, -1
    for i in range(m):
        if pos != 0 and i >= e_i:                        # house bracket from the fill price
            ep = ov[e_i]
            if pos == 1 and (lv[i] <= ep * (1 - sl) or hv[i] >= ep * (1 + tp)):
                pos = 0
            elif pos == -1 and (hv[i] >= ep * (1 + sl) or lv[i] <= ep * (1 - tp)):
                pos = 0
        if pos == 0 and (el[i] or es[i]):
            pos = 1 if el[i] else -1
            e_i = i + 1
            ent[i] = pos
        tgt[i] = pos
    return tgt, ent


def precompute(raw_1m_df, symbol_key, **params):
    return _resample(raw_1m_df, FREQ)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    tgt, ent = _run(bars_df, p)
    prev = np.concatenate(([0], tgt[:-1]))
    le = ent == 1
    lx = (prev == 1) & (tgt == 0)
    se = ent == -1
    sx = (prev == -1) & (tgt == 0)
    return tuple(pd.Series(a, index=bars_df.index) for a in (le, lx, se, sx))


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    _, ent = _run(bars_df, p)
    idx = bars_df.index
    on = pd.Series(ent != 0, index=idx)
    sl = pd.Series(np.where(on, float(p["sl_pct"]) / 100, np.nan), index=idx)
    tp = pd.Series(np.where(on, float(p["tp_pct"]) / 100, np.nan), index=idx)
    return {"sl_stop": sl.shift(1), "tp_stop": tp.shift(1)}


def portfolio_kwargs(**params):
    return {}
