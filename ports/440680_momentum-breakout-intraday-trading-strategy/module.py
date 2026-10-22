"""EMA 5 / 13, MACD, ADX and RSI pivot entries, 5-minute bars: an up-trending set (EMA 5 above 13, rising MACD, ADX above 20, smoothed RSI above 40) goes long, the mirror short, each side at most once in
ten bars; as written every position closes on the bar after its fill.
Port of FMZ strategy #440680 "Momentum Breakout Intraday Trading Strategy" (SPY 1 Minute Day Trader).

FMZ source id: 440680

Source
    https://www.fmz.com/strategy/440680 (PineScript v5, FMZ last modified 2024-02-01 10:32:21).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 156-356), MACD 12 / 26 / 9; RSI 5 with SMA 9; ADX 14 (EMA form); 10-bar cool-down; option stop / target 0.3 (price units)
    buy = ema5 > ema13 and macd < 0.5 and adx > 20 and macd slope > 0 and signal > -0.1 and sma(rsi5, 9) > 40;  short = ema5 < ema13 and macd > -0.5 and adx > 20 and signal < 0 and slope < 0 and rsi signal < 60
    entries need allow_trades and the side's cool-down;  in a position with 6 of 6 conditions: strategy.exit(stop / limit = signal open -/+ 0.3);  position != 0 -> close Pivot Up and Pivot Down (every bar)

Interpretation choices (Pine rules in SURVEY_README.md)
    * Criterion 2: the MACD thresholds are price units (SPY); the port uses fractions of the close at
      the BTC reading near 42000 (0.5 -> 1.19e-5, 0.1 -> 2.4e-6). The cool-downs are kept as written: a
      side may re-enter once the bar time passes its last entry time plus ten bar lengths, and either
      side's reset also re-opens allow_trades. The unconditional close of any held position means each
      trade lasts one bar (filled at the next open, closed at the open after); the 0.3 bracket would
      only fill at that same open and is not ported. A reversing entry on the held bar stands (as
      #438020). REVERSAL INTENDED. No sizing code. FREQ = "5min" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: ADAPT, price-unit MACD levels -> fractions of the close.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used (the hour notes are not coded).
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_440680_pivot_set_one_bar_trades"
FAMILY = "multi_indicator_confluence"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "5min"  # backtest header period: 5m
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "adx_min": [20, 25],
    "cooldown": [10, 20],
}
DEFAULT_PARAMS = {"adx_min": 20, "cooldown": 10, "len": 14, "m_hi": 1.19e-5, "s_lo": 2.4e-6}


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
    up = _rma(d.clip(lower=0), n)
    dn = _rma((-d).clip(lower=0), n)
    with np.errstate(divide="ignore", invalid="ignore"):
        r = 100.0 - 100.0 / (1.0 + up / dn)
    r = r.where(up != 0, 0.0).where(dn != 0, 100.0)    # Pine: down == 0 -> 100, else up == 0 -> 0
    return r.where(up.notna() & dn.notna())


def _emit(tgt, index):
    prev = np.concatenate(([0], tgt[:-1]))
    le = (tgt == 1) & (prev != 1)
    lx = (prev == 1) & (tgt == 0)
    se = (tgt == -1) & (prev != -1)
    sx = (prev == -1) & (tgt == 0)
    return tuple(pd.Series(a, index=index) for a in (le, lx, se, sx))


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    e5, e13 = c.ewm(span=5, adjust=False).mean(), c.ewm(span=13, adjust=False).mean()
    macd = c.ewm(span=12, adjust=False).mean() - c.ewm(span=26, adjust=False).mean()
    sig = macd.ewm(span=9, adjust=False).mean()
    slope = macd - macd.shift(1)
    rs = _rsi(c, 5).rolling(9).mean()
    n = int(p["len"])
    up, dn = h.diff(), -lo.diff()
    pdm = up.where((up > dn) & (up > 0), 0.0).where(up.notna())
    mdm = dn.where((dn > up) & (dn > 0), 0.0).where(dn.notna())
    pc = c.shift(1)
    tr = pd.concat([h - lo, (h - pc).abs(), (lo - pc).abs()], axis=1).max(axis=1)
    etr = tr.ewm(span=n, adjust=False).mean()
    pdi = 100 * pdm.ewm(span=n, adjust=False).mean() / etr
    mdi = 100 * mdm.ewm(span=n, adjust=False).mean() / etr
    dx = 100 * (pdi - mdi).abs() / (pdi + mdi)
    adx = dx.ewm(span=n, adjust=False).mean()
    am = float(p["adx_min"])
    mh, sl_ = float(p["m_hi"]) * c, float(p["s_lo"]) * c
    buy = ((e5 > e13) & (macd < mh) & (adx > am) & (slope > 0) & (sig > -sl_) & (rs > 40)).to_numpy()
    sell = ((e5 < e13) & (macd > -mh) & (adx > am) & (sig < 0) & (slope < 0) & (rs < 60)).to_numpy()
    t = bars_df.index.asi8.astype(float)
    cd = int(p["cooldown"])
    m = len(c)
    tgt = np.zeros(m, dtype=np.int8)
    pos = 0
    allow_l = allow_s = allow_t = True
    lt = st = 0.0
    for i in range(m):
        new = pos
        if buy[i] and allow_t and allow_l:
            new, lt, allow_l, allow_t = 1, t[i], False, False
        if sell[i] and allow_t and allow_s:
            new, st, allow_s, allow_t = -1, t[i], False, False
        step = t[i] - t[i - 1] if i > 0 else 0.0
        if t[i] > lt + step * cd:
            allow_l = allow_t = True
        if t[i] > st + step * cd:
            allow_s = allow_t = True
        if pos != 0 and new == pos:
            new = 0                                      # close Pivot Up / Down on every held bar
        pos = new
        tgt[i] = pos
    return _emit(tgt, bars_df.index)


def portfolio_kwargs(**params):
    return {}
