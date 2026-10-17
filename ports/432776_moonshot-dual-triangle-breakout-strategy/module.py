"""Three SuperTrends against an EMA 233, 10-minute bars: at least two SuperTrends (1 x ATR 10, 2 x ATR 11, 3 x ATR 12) turning
up with all three lines above the EMA goes long, the mirror goes short; two turning against the trade, or a first one
turning against it while all three lines are still on its side, closes it; a 1 % stop from the fill.
Port of FMZ strategy #432776 "Moonshot Dual Triangle Breakout Strategy" (ms hypertrender).

FMZ source id: 432776

Source
    https://www.fmz.com/strategy/432776 (PineScript v5, FMZ last modified 2023-11-21 13:49:10).
    Verbatim copy: original_source.md. Read 2026-10-17 (FMZ-C).

Original signal (original_source.md lines 139-228), SuperTrend 1 / 10, 2 / 11, 3 / 12, EMA 233, stops 1 % / 1 %
    bullish = (d1 up and d2 up) or (d1 up and d3 up) or (d2 up and d3 up) and generaluptrend  (Pine: "and" before "or")
    openlong = (bullish turns on or all-three-up turns on) and generaluptrend;  openshort mirror
    exitlong = (bearish turns on or all-three-down turns on) or (generaluptrend and (bullish or extremebullish)[1] and any SuperTrend down)
    in position: exit(stop = avg x (1 -+ 1 %))

Interpretation choices (Pine rules in SURVEY_README.md)
    * ta.supertrend(factor, atr length) on hl2 with Wilder ATR and the usual band ratchets; direction
      < 0 is up. Pine's "and" binds before "or" in bullish / bearish, as written. generaluptrend =
      all three lines above the EMA 233.
    * The closes are written after both entries and act on the position held at the bar's start; a
      later close of the other side does not undo a reversal: REVERSAL INTENDED. The 1 % stop is a
      fixed fraction of the fill, live on the fill bar in the house engine (Pine places it once a
      position exists). The port's state machine follows the house stop on bars. Stop module:
      portfolio_kwargs {} (driver D4). FREQ = "10min" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; stop fixed at entry.
    2 generic: PASS, SuperTrend states, an EMA and a percentage stop of the fill.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code; the stops quoted in original_sizing.txt.
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

NAME = "fmz_432776_triple_supertrend_ema"
FAMILY = "supertrend"  # proposed 2026-10-17 (FMZ-C), user to confirm
FREQ = "10min"  # backtest header period: 10m
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "ema_len": [233, 100],
    "sl_pct": [1.0, 2.0],
}
DEFAULT_PARAMS = {"f1": 1.0, "a1": 10, "f2": 2.0, "a2": 11, "f3": 3.0, "a3": 12, "ema_len": 233, "sl_pct": 1.0}


def _resample(raw_1m_df, freq):
    ohlc = raw_1m_df[["open", "high", "low", "close"]]
    bars = ohlc.resample(freq, label="left", closed="left").agg(
        {"open": "first", "high": "max", "low": "min", "close": "last"})
    bars = bars.dropna(how="all")  # an empty period is not a bar; never forward-filled
    if bars.index.tz is None:
        raise ValueError("raw_1m_df must have a tz-aware UTC index")
    return bars


def _supertrend(h, lo, c, factor, n):
    """Pine ta.supertrend: (line, direction), direction -1 = up, 1 = down."""
    c1 = c.shift(1)
    tr = pd.concat([h - lo, (h - c1).abs(), (lo - c1).abs()], axis=1).max(axis=1)
    atr = tr.ewm(alpha=1 / n, adjust=False).mean().to_numpy()
    hl2 = ((h + lo) / 2).to_numpy()
    cv = c.to_numpy(dtype=float)
    m = len(cv)
    st, dr = np.full(m, np.nan), np.ones(m)
    pu = pl = pst = np.nan
    for i in range(m):
        up, lw = hl2[i] + factor * atr[i], hl2[i] - factor * atr[i]
        if i >= 1 and not np.isnan(pl):
            lw = lw if (lw > pl or cv[i - 1] < pl) else pl
            up = up if (up < pu or cv[i - 1] > pu) else pu
        if i == 0 or np.isnan(atr[i - 1]):
            d = 1.0
        elif pst == pu:
            d = -1.0 if cv[i] > up else 1.0
        else:
            d = 1.0 if cv[i] < lw else -1.0
        s = lw if d == -1 else up
        st[i], dr[i] = s, d
        pu, pl, pst = up, lw, s
    return pd.Series(st, index=c.index), pd.Series(dr, index=c.index)


def _run(bars_df, p):
    o, h, lo, c = (bars_df[k] for k in ("open", "high", "low", "close"))
    s1, d1 = _supertrend(h, lo, c, float(p["f1"]), int(p["a1"]))
    s2, d2 = _supertrend(h, lo, c, float(p["f2"]), int(p["a2"]))
    s3, d3 = _supertrend(h, lo, c, float(p["f3"]), int(p["a3"]))
    e = c.ewm(span=int(p["ema_len"]), adjust=False).mean()
    gup = (s1 > e) & (s2 > e) & (s3 > e)
    gdn = (s1 < e) & (s2 < e) & (s3 < e)
    u1, u2, u3 = d1 < 0, d2 < 0, d3 < 0
    w1, w2, w3 = d1 > 0, d2 > 0, d3 > 0
    bull = (u1 & u2) | (u1 & u3) | (u2 & u3 & gup)
    xbull = u1 & u2 & u3 & gup
    bear = (w1 & w2) | (w1 & w3) | (w2 & w3 & gdn)
    xbear = w1 & w2 & w3 & gdn
    on = lambda x: x & ~x.shift(1, fill_value=False)  # noqa: E731
    tp_l = ((gup & bull.shift(1, fill_value=False)) | (gup & xbull.shift(1, fill_value=False))) & (w1 | w2 | w3)
    tp_s = ((gdn & bear.shift(1, fill_value=False)) | (gdn & xbear.shift(1, fill_value=False))) & (u1 | u2 | u3)
    ol = ((on(bull) | on(xbull)) & gup).to_numpy()
    os_ = ((on(bear) | on(xbear)) & gdn).to_numpy()
    xl = (on(xbear) | on(bear) | tp_l).to_numpy()
    xs = (on(xbull) | on(bull) | tp_s).to_numpy()
    ov, hv, lv = o.to_numpy(dtype=float), h.to_numpy(dtype=float), lo.to_numpy(dtype=float)
    sl = float(p["sl_pct"]) / 100
    m = len(ov)
    tgt = np.zeros(m, dtype=np.int8)
    ent = np.zeros(m, dtype=np.int8)
    pos, e_i = 0, -1
    for i in range(m):
        if pos != 0 and i >= e_i:                        # house stop from the fill price
            ep = ov[e_i]
            if (pos == 1 and lv[i] <= ep * (1 - sl)) or (pos == -1 and hv[i] >= ep * (1 + sl)):
                pos = 0
        start = pos
        if ol[i]:
            pos = 1
        if os_[i]:
            pos = -1
        if xl[i] and start == 1 and pos == 1:
            pos = 0
        if xs[i] and start == -1 and pos == -1:
            pos = 0
        if pos != 0 and pos != start:
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
    sl = pd.Series(np.where(ent != 0, float(p["sl_pct"]) / 100, np.nan), index=bars_df.index)
    return {"sl_stop": sl.shift(1)}


def portfolio_kwargs(**params):
    return {}
