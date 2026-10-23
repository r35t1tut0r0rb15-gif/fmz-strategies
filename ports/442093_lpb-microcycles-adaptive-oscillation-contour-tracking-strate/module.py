"""Hourly bars, long only: from flat, the Hodrick-Prescott end-point filter of ohlc4 (lambda 1000, last 100 bars) crossing over ohlc4 goes long, with a stop 1 ATR 14 under the lower of the last two lows and a target the same distance above the close; the bracket ends the trade.
Port of FMZ strategy #442093 "LPB Microcycles Adaptive Oscillation Contour Tracking Strategy" (LPB MicroCycles Strategy (HPVWAP)).

FMZ source id: 442093

Source
    https://www.fmz.com/strategy/442093 (PineScript v4, FMZ last modified 2024-02-19 11:32:12).
    Verbatim copy: original_source.md. Read 2026-10-23 (FMZ-C).

Original signal (original_source.md lines 147-335), lambda 1000; filter length 100; VWAP timeframe '1'; stop ATR x 1; R:R 1
    HP = x[0] of the pentadiagonal HP solve over src[0 .. 99];  start = security(tickerid, '1', time);  myvwap resets when start changes
    Long = crossover(av, ohlc4);  validLong = Long and position_size == 0 -> entry Long, t_stop = (low < low[1] ? low : low[1]) - atr, t_target = close + (close - t_stop);  exit(limit = t_target, stop = t_stop)

Interpretation choices (Pine rules in SURVEY_README.md)
    * The HP solve depends only on lambda and the length, so its end value is a fixed weighted sum of
      the last 100 ohlc4 values; the port runs the script's own elimination once on unit vectors to get
      those weights. The "VWAP" restarts whenever the 1-minute security() time changes, i.e. on every
      hourly bar, so it equals the HP value itself and volume cancels out (held for volume, not used).
      The security() reads only the time of the last minute, not a price. The short setup has no order.
      The bracket levels are fixed at the signal bar: ported as fractions of the fill (exact; a level the
      fill has passed is taken at once, 1e-6 floor); Pine sends them from the fill bar's close, the port
      arms them at the fill, and the signals follow them for the flat test. Long only. 100 % of equity is
      sizing. Stop module: portfolio_kwargs {} (driver D4). FREQ = "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; bracket at the signal bar as fractions of the fill.
    2 generic: PASS, Hodrick-Prescott filter crossing over price with a swing / ATR bracket.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: strategy(): 100 % of equity, not ported.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: none (the VWAP resets every bar).
Long only.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_442093_hp_filter_cross_over_price_swing_atr_bracket_1h_long_only"
FAMILY = "regression_bands"  # proposed 2026-10-23 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "lam": [1000.0, 100.0],
    "rr": [1.0, 2.0],
}
DEFAULT_PARAMS = {"lam": 1000.0, "leng": 100, "stop_mult": 1.0, "rr": 1.0, "atr_len": 14}


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


def _hp_weights(lam, leng):
    """The script's pentadiagonal elimination run on unit vectors: x[0] = weights @ src[0 .. leng-1]
    (src[k] = k bars ago)."""
    a = np.full(leng, lam * -4.0)
    c = np.full(leng, lam * -4.0)
    d = np.full(leng, lam * 6.0 + 1.0)
    e = np.full(leng, lam)
    f = np.full(leng, lam)
    b = np.eye(leng)
    ll1, ll2 = leng - 1, leng - 2
    d[0] = d[ll1] = lam + 1.0
    d[1] = d[ll2] = lam * 5.0 + 1.0
    c[0] = c[ll2] = lam * -2.0
    a[0] = a[ll2] = lam * -2.0
    r, s, t = a[0], a[1], e[0]
    for i in range(1, ll2 + 1):
        xm = r / d[i - 1]
        d[i] -= xm * c[i - 1]
        c[i] -= xm * f[i - 1]
        b[i] = b[i] - xm * b[i - 1]
        xm = t / d[i - 1]
        r = s - xm * c[i - 1]
        d[i + 1] -= xm * f[i - 1]
        b[i + 1] = b[i + 1] - xm * b[i - 1]
        s = a[i + 1]
        t = e[i]
    xm = r / d[ll2]
    d[ll1] -= xm * c[ll2]
    x = np.zeros((leng, leng))
    x[ll1] = (b[ll1] - xm * b[ll2]) / d[ll1]
    x[ll2] = (b[ll2] - c[ll2] * x[ll1]) / d[ll2]
    for j in range(leng - 2):
        i = leng - 3 - j
        x[i] = (b[i] - f[i] * x[i + 2] - c[i] * x[i + 1]) / d[i]
    return x[0]


def _levels(bars_df, p):
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    pc = c.shift(1)
    tr = pd.concat([h - lo, (h - pc).abs(), (lo - pc).abs()], axis=1).max(axis=1).where(pc.notna())
    stop_size = _rma(tr, int(p["atr_len"])) * float(p["stop_mult"])
    stop_px = lo.where(lo < lo.shift(1), lo.shift(1)) - stop_size
    target_px = c + (c - stop_px) * float(p["rr"])
    return stop_px, target_px


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    o, h, lo, c = (bars_df[k] for k in ("open", "high", "low", "close"))
    src = (o + h + lo + c) / 4
    n = int(p["leng"])
    w = _hp_weights(float(p["lam"]), n)
    sv = src.to_numpy(dtype=float)
    hp = np.full(len(sv), np.nan)
    if len(sv) >= n:
        hp[n - 1:] = np.lib.stride_tricks.sliding_window_view(sv, n)[:, ::-1] @ w   # column k = k bars ago
    av = pd.Series(hp, index=c.index)
    cross = ((av > src) & (av.shift(1) <= src.shift(1))).to_numpy()
    stop_px, target_px = _levels(bars_df, p)
    stv, tgv = stop_px.to_numpy(), target_px.to_numpy()
    hv, lv = h.to_numpy(dtype=float), lo.to_numpy(dtype=float)
    m = len(cross)
    le = np.zeros(m, dtype=bool)
    pos, pend, sl_px, tp_px = 0, False, np.nan, np.nan
    for i in range(m):
        if pend:
            pos, pend = 1, False
        if pos == 1 and (lv[i] <= sl_px or hv[i] >= tp_px):   # the bracket ends the trade inside the bar
            pos = 0
        if pos == 0 and not pend and cross[i] and i + 1 < m:
            le[i], pend, sl_px, tp_px = True, True, stv[i], tgv[i]
    ix = bars_df.index
    false = pd.Series(False, index=ix)
    return pd.Series(le, index=ix), false, false.copy(), false.copy()


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    le, lx, se, sx = simulate(bars_df, **params)
    o = bars_df["open"]
    stop_px, target_px = _levels(bars_df, p)
    lf = le.shift(1, fill_value=False)
    sl_f = (1 - stop_px.shift(1) / o).where(lf)
    tp_f = (target_px.shift(1) / o - 1).where(lf)
    return {"sl_stop": sl_f.clip(lower=1e-6), "tp_stop": tp_f.clip(lower=1e-6)}


def portfolio_kwargs(**params):
    return {}
