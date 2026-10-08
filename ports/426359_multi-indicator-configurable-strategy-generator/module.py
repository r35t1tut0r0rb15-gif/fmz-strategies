"""Strategy Creator (defaults): from flat, go long when EMA 50 > 100 > 200, RSI < 48, %K > %D,
the MACD histogram < 0 and ADX > 25, unless the last 3 closed trades were all longs; shorts
mirrored (RSI > 52, %K < %D, histogram > 0). Each trade has a 0.4 % stop and a 0.5 % target.
Port of FMZ strategy #426359 "Multi Indicator Configurable Strategy Generator".

Source
    https://www.fmz.com/strategy/426359 (PineScript v5, FMZ last modified 2023-09-11 14:33:12).
    Verbatim copy: original_source.md. Read 2026-10-07.

Original signal (original_source.md lines 124-490), all filters on, 3 trades in one direction
    EMA: ema50 > ema100 > ema200 (long) / < < (short)
    RSI(14) (down == 0 ? 100 : up == 0 ? 0 : Pine formula) < 48 long / > 52 short
    stoch: k = sma(stoch(14), 1), d = sma(k, 3); k > d long / k < d short
    MACD 12 / 26 / 9 (EMA): hist < 0 long / hist > 0 short
    ADX(14, 14) > 25 both sides
    TRADESINAROW: long allowed if any of the last 3 closed trades was short (missing = allowed)
    opentrades == 0 -> entry;  exit(stop = avg * (1 -+ 0.4 %), limit = avg * (1 +- 0.5 %))

Interpretation choices (Pine rules in SURVEY_README.md)
    * strategy.closedtrades.size(k) with k < 0 (fewer closed trades than looked back) is read as
      na, so nz() makes it count as "allowed", as for no trade at all.
    * The stop / limit are fractions of the fill price (sl_stop / tp_stop). Entries need a flat
      position, so simulate() mirrors the engine's stop and target from the fill bar on; the sign
      of each closed trade feeds the 3-in-a-row filter. Opposite entries cannot occur while a
      position is open (entries only from flat; portfolio_kwargs upon_opposite_entry "ignore").
    * The test-period window (2023) is a backtest window: dropped. The MACD time-frame input,
      the RSI MA and the histogram averages (off by default) do not reach the orders.
    * FREQ = "5min" from the backtest header.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_426359_strategy_creator_confluence"
FAMILY = "multi_indicator_confluence"  # proposed 2026-10-07, user to confirm
FREQ = "5min"  # backtest header period: 5m
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "sl_pct": [0.4, 0.8],
    "tp_pct": [0.5, 1.0],
    "max_in_row": [1, 3],
}
DEFAULT_PARAMS = {"ema_fast": 50, "ema_mid": 100, "ema_slow": 200, "rsi_len": 14, "rsi_long": 48,
                  "rsi_short": 52, "k_len": 14, "k_smooth": 1, "d_len": 3, "macd_fast": 12,
                  "macd_slow": 26, "macd_sig": 9, "adx_len": 14, "di_len": 14, "adx_min": 25,
                  "sl_pct": 0.4, "tp_pct": 0.5, "max_in_row": 3}


def _resample(raw_1m_df, freq):
    ohlc = raw_1m_df[["open", "high", "low", "close"]]
    bars = ohlc.resample(freq, label="left", closed="left").agg(
        {"open": "first", "high": "max", "low": "min", "close": "last"})
    bars = bars.dropna(how="all")  # an empty period is not a bar; never forward-filled
    if bars.index.tz is None:
        raise ValueError("raw_1m_df must have a tz-aware UTC index")
    return bars


def _rma(x, n):
    """Wilder smoothing as TA-Lib: SMA seed over the first n valid values, then recursive."""
    v = x.to_numpy(dtype=float)
    out = np.full(v.shape, np.nan)
    valid = np.flatnonzero(~np.isnan(v))
    if len(valid) >= n:
        s = valid[0]
        out[s + n - 1] = v[s:s + n].mean()
        for i in range(s + n, len(v)):
            out[i] = (out[i - 1] * (n - 1) + v[i]) / n
    return pd.Series(out, index=x.index)


def _rsi_pine(close, n):
    """rsi() as Pine defines it: 100 when the average loss is 0, 0 when the average gain is 0."""
    d = close.diff()
    up, down = _rma(d.clip(lower=0), n), _rma((-d).clip(lower=0), n)
    rsi = 100.0 - 100.0 / (1.0 + up / down)
    return rsi.mask(up == 0, 0.0).mask(down == 0, 100.0).where(up.notna() & down.notna())


def _fixnan(v):
    """Pine fixnan: replace na by the last non-na value (past values only)."""
    out = np.array(v, dtype=float)
    for i in range(1, len(out)):
        if np.isnan(out[i]):
            out[i] = out[i - 1]
    return out


def _adx_pine(bars, di_len, adx_len):
    """Pine's built-in-style dirmov/adx: RMA smoothing, fixnan on DI+/DI-."""
    h, lo, c = bars["high"], bars["low"], bars["close"]
    up, down = h.diff(), -lo.diff()
    plus_dm = np.where(up.isna(), np.nan, np.where((up > down) & (up > 0), up, 0.0))
    minus_dm = np.where(down.isna(), np.nan, np.where((down > up) & (down > 0), down, 0.0))
    pc = c.shift(1)
    tr = pd.concat([h - lo, (h - pc).abs(), (lo - pc).abs()], axis=1).max(axis=1, skipna=False)
    trs = _rma(tr, di_len)
    plus = _fixnan((100 * _rma(pd.Series(plus_dm, index=h.index), di_len) / trs).to_numpy())
    minus = _fixnan((100 * _rma(pd.Series(minus_dm, index=h.index), di_len) / trs).to_numpy())
    s = plus + minus
    dx = pd.Series(np.abs(plus - minus) / np.where(s == 0, 1, s), index=h.index)
    return pd.Series(plus, index=h.index), pd.Series(minus, index=h.index), 100 * _rma(dx, adx_len)


def _conditions(bars, p):
    h, l, c = bars["high"], bars["low"], bars["close"]
    ema = lambda x, n: x.ewm(span=int(n), adjust=False).mean()
    e1, e2, e3 = ema(c, p["ema_fast"]), ema(c, p["ema_mid"]), ema(c, p["ema_slow"])
    rsi = _rsi_pine(c, int(p["rsi_len"]))
    n = int(p["k_len"])
    lo, hi = l.rolling(n).min(), h.rolling(n).max()
    k = (100 * (c - lo) / (hi - lo)).rolling(int(p["k_smooth"])).mean()
    d = k.rolling(int(p["d_len"])).mean()
    macd = ema(c, p["macd_fast"]) - ema(c, p["macd_slow"])
    hist = macd - ema(macd, p["macd_sig"])
    _, _, adx = _adx_pine(bars, int(p["di_len"]), int(p["adx_len"]))
    strong = adx > p["adx_min"]
    long_c = (e1 > e2) & (e2 > e3) & (rsi < p["rsi_long"]) & (k > d) & (hist < 0) & strong
    short_c = (e1 < e2) & (e2 < e3) & (rsi > p["rsi_short"]) & (k < d) & (hist > 0) & strong
    return long_c.to_numpy(), short_c.to_numpy()


def precompute(raw_1m_df, symbol_key, **params):
    return _resample(raw_1m_df, FREQ)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    long_c, short_c = _conditions(bars_df, p)
    o, h, lo = (bars_df[k].to_numpy(dtype=float) for k in ("open", "high", "low"))
    sl, tp = p["sl_pct"] / 100, p["tp_pct"] / 100
    k = int(p["max_in_row"])
    m = len(o)
    le, se = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    pos, pending, stop, target = 0, 0, np.nan, np.nan
    closed = []  # signs of closed trades, oldest first
    for i in range(m):
        if pending:
            pos, e = pending, o[i]
            stop, target = e * (1 - pos * sl), e * (1 + pos * tp)
            pending = 0
        if pos == 1 and (lo[i] <= stop or h[i] >= target):
            closed.append(1)
            pos = 0
        elif pos == -1 and (h[i] >= stop or lo[i] <= target):
            closed.append(-1)
            pos = 0
        if pos == 0 and not pending:
            last = closed[-k:] if len(closed) >= k else None
            long_ok = last is None or min(last) < 0
            short_ok = last is None or max(last) > 0
            if long_c[i] and long_ok:
                le[i], pending = True, 1
            elif short_c[i] and short_ok:
                se[i], pending = True, -1
    idx = bars_df.index
    false = pd.Series(False, index=idx)
    return pd.Series(le, index=idx), false.copy(), pd.Series(se, index=idx), false.copy()


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    return {"sl_stop": p["sl_pct"] / 100, "tp_stop": p["tp_pct"] / 100}


def portfolio_kwargs(**params):
    return {"upon_opposite_entry": "ignore"}
