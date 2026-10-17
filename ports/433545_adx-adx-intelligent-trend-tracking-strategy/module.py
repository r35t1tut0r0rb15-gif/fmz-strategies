"""Low-ADX box breakouts with a box-sized bracket, 5-minute bars: while flat and the ADX 14 is under 18, a close crossing the
top of the previous 20-bar box goes long and a close crossing its bottom goes short; the target is 1 box width and the
stop half a box width from the entry, the box frozen while a position is open.
Port of FMZ strategy #433545 "ADX智能趋势跟踪策略ADX-Intelligent-Trend-Tracking-Strategy" (Rob Booker - ADX Breakout (ADX Breakout V5)).

FMZ source id: 433545

Source
    https://www.fmz.com/strategy/433545 (PineScript v5, FMZ last modified 2023-11-28 14:04:00).
    Verbatim copy: original_source.md. Read 2026-10-17 (FMZ-C).

Original signal (original_source.md lines 137-216), ADX 14 / 14, lower level 18; box lookback 20; target 1.0 x box width, stop 0.5 x box width; both directions
    box = flat ? highest(high, 20)[1] / lowest(low, 20)[1] : the carried box;  width = upper - lower
    flat and cross(close, upper) and adx < 18 -> entry long;  flat and cross(close, lower) and adx < 18 -> entry short
    exit(limit = avg +/- 1.0 width, stop = avg -/+ 0.5 width)

Interpretation choices (Pine rules in SURVEY_README.md)
    * ta.cross is a cross in either direction, as written. The bracket uses the box of the signal bar
      (the box is carried from it while in the position): tp_mult / sl_mult x width / close of the
      signal bar, shifted one bar inside stops() and re-based on the fill.
    * Entries need a flat position. The engine runs the bracket; simulate() tracks the same bracket on
      the bars' highs and lows (from the bar after the fill, as the source and the engine do) only to
      know when the source is flat again and when the box is frozen. A bar crossing both box edges
      ends short (the short entry is issued last).
    * Opposite entries cannot occur (entries only from flat). Stop module: portfolio_kwargs {}
      (driver D4). FREQ = "5min" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; bracket fixed at entry.
    2 generic: PASS, box breaks, ADX level and box-width exits.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: the strategy() 100000 cash quantity stored.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
Opposite entries cannot occur.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_433545_adx_box_breakout_bracket"
FAMILY = "donchian_breakout"  # proposed 2026-10-17 (FMZ-C), user to confirm
FREQ = "5min"  # backtest header period: 5m
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "box_len": [20, 40],
    "adx_level": [18, 25],
}
DEFAULT_PARAMS = {"adx_len": 14, "adx_smooth": 14, "adx_level": 18, "box_len": 20, "tp_mult": 1.0, "sl_mult": 0.5}


def _resample(raw_1m_df, freq):
    ohlc = raw_1m_df[["open", "high", "low", "close"]]
    bars = ohlc.resample(freq, label="left", closed="left").agg(
        {"open": "first", "high": "max", "low": "min", "close": "last"})
    bars = bars.dropna(how="all")  # an empty period is not a bar; never forward-filled
    if bars.index.tz is None:
        raise ValueError("raw_1m_df must have a tz-aware UTC index")
    return bars


def _fixnan(v):
    out = v.copy()
    last = np.nan
    for i in range(len(out)):
        if np.isnan(out[i]):
            out[i] = last
        else:
            last = out[i]
    return out


def _adx(bars_df, dilen, adxlen):
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    up, dn = h.diff(), -lo.diff()
    c1 = c.shift(1)
    tr = pd.concat([h - lo, (h - c1).abs(), (lo - c1).abs()], axis=1).max(axis=1)
    trur = tr.ewm(alpha=1 / dilen, adjust=False).mean()
    pdm = pd.Series(np.where((up > dn) & (up > 0), up, 0.0), index=c.index).ewm(alpha=1 / dilen, adjust=False).mean()
    mdm = pd.Series(np.where((dn > up) & (dn > 0), dn, 0.0), index=c.index).ewm(alpha=1 / dilen, adjust=False).mean()
    with np.errstate(invalid="ignore", divide="ignore"):
        plus = _fixnan((100 * pdm / trur).replace([np.inf, -np.inf], np.nan).to_numpy())
        minus = _fixnan((100 * mdm / trur).replace([np.inf, -np.inf], np.nan).to_numpy())
    s = plus + minus
    dx = pd.Series(np.abs(plus - minus) / np.where(s == 0, 1.0, s), index=c.index)
    return (100 * dx.ewm(alpha=1 / adxlen, adjust=False).mean()).to_numpy()


def _signals(bars_df, p):
    o = bars_df["open"].to_numpy(dtype=float)
    h = bars_df["high"].to_numpy(dtype=float)
    lo = bars_df["low"].to_numpy(dtype=float)
    c = bars_df["close"].to_numpy(dtype=float)
    n = int(p["box_len"])
    hh = bars_df["high"].rolling(n).max().shift(1).to_numpy()
    ll = bars_df["low"].rolling(n).min().shift(1).to_numpy()
    adx = _adx(bars_df, int(p["adx_len"]), int(p["adx_smooth"]))
    low_adx = adx < float(p["adx_level"])
    tpm, slm = float(p["tp_mult"]), float(p["sl_mult"])
    m = len(c)
    le, se = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    frac_w = np.full(m, np.nan)
    bu = bl = np.nan
    bu_prev = bl_prev = np.nan
    pos, entry, width, fill_bar = 0, np.nan, np.nan, -1
    pending = 0
    for i in range(m):
        if pending != 0:                      # the signal of bar i - 1 fills at this bar's open
            pos, entry, fill_bar, pending = pending, o[i], i, 0
        if pos != 0 and i > fill_bar:         # the bracket is live from the bar after the fill
            if pos == 1 and (lo[i] <= entry - slm * width or h[i] >= entry + tpm * width):
                pos = 0
            elif pos == -1 and (h[i] >= entry + slm * width or lo[i] <= entry - tpm * width):
                pos = 0
        flat = pos == 0
        if flat:
            bu, bl = hh[i], ll[i]
        w_now = bu - bl
        with np.errstate(invalid="ignore"):
            xu = (c[i] > bu and c[i - 1] <= bu_prev) or (c[i] < bu and c[i - 1] >= bu_prev) if i > 0 else False
            xl = (c[i] > bl and c[i - 1] <= bl_prev) or (c[i] < bl and c[i - 1] >= bl_prev) if i > 0 else False
        if flat and low_adx[i]:
            if xl:
                se[i], pending = True, -1
            elif xu:
                le[i], pending = True, 1
            if pending != 0:
                width = w_now
                frac_w[i] = w_now / c[i]
        bu_prev, bl_prev = bu, bl
    return le, se, frac_w


def precompute(raw_1m_df, symbol_key, **params):
    return _resample(raw_1m_df, FREQ)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    le, se, _ = _signals(bars_df, p)
    ix = bars_df.index
    false = pd.Series(False, index=ix)
    return pd.Series(le, index=ix), false, pd.Series(se, index=ix), false.copy()


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    _, _, fw = _signals(bars_df, p)
    w = pd.Series(fw, index=bars_df.index)
    return {"sl_stop": (w * float(p["sl_mult"])).shift(1), "tp_stop": (w * float(p["tp_mult"])).shift(1)}


def portfolio_kwargs(**params):
    return {}
