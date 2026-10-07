"""QQE-MOD + SSL Hybrid + Waddah Attar Explosion confluence entries, swing stop, exit on the SSL
exit-line cross while in profit.
Port of FMZ strategy #361969 "QQE-MOD-SSL-Hybrid-Waddah-Attar-Explosion".

Source
    https://www.fmz.com/strategy/361969 (PineScript v5, FMZ last modified 2022-05-09 12:01:14).
    Verbatim copy: original_source.md. Read 2026-10-07.

Original signal (original_source.md lines 158-583; defaults)
    QQE1: RSI(6) -> EMA 6 = RsiMa; QQE bands (factor 3); BB(50, 0.35) on (QQE line - 50)
    QQE2: RSI(6) -> EMA 5 = RsiMa2
    qqeBuy = (RsiMa2-50 > 3 and RsiMa-50 > upper) and not the same on the previous bar
    sslBuy = close > HMA(close,60) + 0.2*EMA(TR,60) and close > HMA(close,60)
    waeBuy = t1 > 0 and t1 > e1, t1 = 180*change of MACD(20,40), e1 = BB(20,2) width
    flat and qqeBuy and sslBuy and waeBuy -> long, stop = lowest(low,10) at entry
    long and crossover(sslExit, close) and trade in profit -> close   (short side mirror)
    sslExit: HMA(15) of high/low with the SSL state switch

Interpretation choices (Pine rules in SURVEY_README.md)
    * The swing stop is fixed at entry: stops() returns sl_stop = (close - lowest(low,10)) /
      close of the signal bar (short: highest(high,10)), shifted one bar inside stops(); vbt
      applies it to the fill price. Bars are 4 h: mark coarse_bar_stop (rule 4).
    * Entries need a flat position, so simulate() mirrors the engine's stop to know when the
      position is gone: from the fill bar on, a low (high) through fill*(1 -/+ stop fraction)
      means stopped out. No exit signal is emitted for it (the engine exits). "In profit" for
      the exit is close above (below) the fill price.
    * HMA lengths: len/2 for len 15 is truncated to 7 (Pine needs an int length).
    * The date-range inputs are a backtest window (dropped); risk-based qty is sizing.
    * Entries only from flat: opposite entries cannot occur; portfolio_kwargs returns
      upon_opposite_entry="ignore" (rule 6). FREQ = "4h" from the backtest header.

Marks: coarse_bar_stop
"""
import numpy as np
import pandas as pd

NAME = "fmz_361969_qqe_ssl_wae_confluence"
FAMILY = "multi_indicator_confluence"  # proposed 2026-10-07, user to confirm
FREQ = "4h"  # backtest header period: 4h
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "baseline_len": [40, 60, 90],
    "swing_len": [5, 10, 20],
    "sensitivity": [120, 180],
}
DEFAULT_PARAMS = {"baseline_len": 60, "swing_len": 10, "sensitivity": 180, "exit_len": 15,
                  "rsi1": 6, "sf1": 6, "qqe1": 3.0, "bb_len": 50, "bb_mult": 0.35,
                  "rsi2": 6, "sf2": 5, "thresh2": 3.0, "kelt_mult": 0.2,
                  "wae_fast": 20, "wae_slow": 40, "wae_bb": 20, "wae_mult": 2.0}


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


def _rsi(close, n):
    d = close.diff()
    return 100.0 - 100.0 / (1.0 + _rma(d.clip(lower=0), n) / _rma((-d).clip(lower=0), n))


def _wma(x, n):
    """ta.wma: linearly weighted MA, weight n on the current bar."""
    n = int(n)
    w = np.arange(1, n + 1, dtype=float)
    return x.rolling(n).apply(lambda a: np.dot(a, w) / w.sum(), raw=True)


def _hma(x, n):
    return _wma(2 * _wma(x, int(n / 2)) - _wma(x, n), int(round(np.sqrt(n))))


def _qqe_line(rsima, factor, wilders):
    atr_rsi = (rsima.shift(1) - rsima).abs()
    dar = atr_rsi.ewm(span=wilders, adjust=False, ignore_na=True).mean()
    dar = dar.ewm(span=wilders, adjust=False, ignore_na=True).mean() * factor
    r, d = rsima.to_numpy(), dar.to_numpy()
    m = len(r)
    lb, sb, tl = np.full(m, np.nan), np.full(m, np.nan), np.full(m, np.nan)
    trend = 1
    for t in range(m):
        nl, ns = r[t] - d[t], r[t] + d[t]
        if t > 0 and r[t - 1] > lb[t - 1] and r[t] > lb[t - 1]:
            lb[t] = max(lb[t - 1], nl)
        else:
            lb[t] = nl
        if t > 0 and r[t - 1] < sb[t - 1] and r[t] < sb[t - 1]:
            sb[t] = min(sb[t - 1], ns)
        else:
            sb[t] = ns
        if t >= 2:
            def cross(a1, a0, b1, b0):
                return (a1 > b1 and a0 <= b0) or (a1 < b1 and a0 >= b0)
            if cross(r[t], r[t - 1], sb[t - 1], sb[t - 2]):
                trend = 1
            elif cross(lb[t - 1], lb[t - 2], r[t], r[t - 1]):
                trend = -1
        tl[t] = lb[t] if trend == 1 else sb[t]
    return pd.Series(tl, index=rsima.index)


def _ssl_line(close, hi_ma, lo_ma):
    c, h, lo = close.to_numpy(), hi_ma.to_numpy(), lo_ma.to_numpy()
    out = np.full(len(c), np.nan)
    hlv = np.nan
    for t in range(len(c)):
        hlv = 1 if c[t] > h[t] else (-1 if c[t] < lo[t] else hlv)
        out[t] = h[t] if hlv < 0 else lo[t]
    return pd.Series(out, index=close.index)


def precompute(raw_1m_df, symbol_key, **params):
    return _resample(raw_1m_df, FREQ)


def _conditions(bars_df, p):
    c, h, lo = bars_df["close"], bars_df["high"], bars_df["low"]
    rsima = _rsi(c, int(p["rsi1"])).ewm(span=int(p["sf1"]), adjust=False, ignore_na=True).mean()
    tl = _qqe_line(rsima, p["qqe1"], int(p["rsi1"]) * 2 - 1) - 50
    basis = tl.rolling(int(p["bb_len"])).mean()
    dev = p["bb_mult"] * tl.rolling(int(p["bb_len"])).std(ddof=0)
    rsima2 = _rsi(c, int(p["rsi2"])).ewm(span=int(p["sf2"]), adjust=False, ignore_na=True).mean()
    green = (rsima2 - 50 > p["thresh2"]) & (rsima - 50 > basis + dev)
    red = (rsima2 - 50 < -p["thresh2"]) & (rsima - 50 < basis - dev)
    qqe_buy = green & ~green.shift(1, fill_value=False)
    qqe_sell = red & ~red.shift(1, fill_value=False)
    n = int(p["baseline_len"])
    bbmc = _hma(c, n)
    pc = c.shift(1)
    tr = pd.concat([h - lo, (h - pc).abs(), (lo - pc).abs()], axis=1).max(axis=1, skipna=False)
    rng = tr.ewm(span=n, adjust=False, ignore_na=True).mean()
    ssl_buy = (c > bbmc + rng * p["kelt_mult"]) & (c > bbmc)
    ssl_sell = (c < bbmc - rng * p["kelt_mult"]) & (c < bbmc)
    macd = c.ewm(span=int(p["wae_fast"]), adjust=False).mean() - c.ewm(span=int(p["wae_slow"]), adjust=False).mean()
    t1 = (macd - macd.shift(1)) * p["sensitivity"]
    e1 = 2 * p["wae_mult"] * c.rolling(int(p["wae_bb"])).std(ddof=0)
    wae_buy = (t1 > 0) & (t1 > e1)
    wae_sell = (t1 < 0) & (-t1 > e1)
    ssl_exit = _ssl_line(c, _hma(h, int(p["exit_len"])), _hma(lo, int(p["exit_len"])))
    x_long = (c > ssl_exit) & (c.shift(1) <= ssl_exit.shift(1))      # crossover(close, sslExit)
    x_short = (ssl_exit > c) & (ssl_exit.shift(1) <= c.shift(1))     # crossover(sslExit, close)
    long_c = (qqe_buy & ssl_buy & wae_buy).to_numpy()
    short_c = (qqe_sell & ssl_sell & wae_sell).to_numpy()
    return long_c, short_c, x_long.to_numpy(), x_short.to_numpy()


def _stop_fraction(bars_df, p):
    c = bars_df["close"]
    n = int(p["swing_len"])
    long_f = (c - bars_df["low"].rolling(n).min()) / c
    short_f = (bars_df["high"].rolling(n).max() - c) / c
    return long_f, short_f


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    long_c, short_c, x_long, x_short = _conditions(bars_df, p)
    lf, sf = (s.to_numpy() for s in _stop_fraction(bars_df, p))
    o, h, lo, c = (bars_df[k].to_numpy(dtype=float) for k in ("open", "high", "low", "close"))

    m = len(c)
    le, lx, se, sx = (np.zeros(m, dtype=bool) for _ in range(4))
    pos, pending, frac, entry, stop = 0, 0, np.nan, np.nan, np.nan
    for i in range(m):
        if pending:
            pos, entry, pending = pending, o[i], 0
            stop = entry * (1 - frac) if pos == 1 else entry * (1 + frac)
        if pos == 1 and lo[i] <= stop:            # engine's sl_stop fires: flat from here
            pos = 0
        elif pos == -1 and h[i] >= stop:
            pos = 0
        if pos == 0:
            if long_c[i] and not np.isnan(lf[i]):
                le[i], pending, frac = True, 1, lf[i]
            elif short_c[i] and not np.isnan(sf[i]):
                se[i], pending, frac = True, -1, sf[i]
        elif pos == 1 and x_short[i] and c[i] > entry:
            lx[i], pos = True, 0
        elif pos == -1 and x_long[i] and c[i] < entry:
            sx[i], pos = True, 0

    idx = bars_df.index
    return (pd.Series(le, index=idx), pd.Series(lx, index=idx),
            pd.Series(se, index=idx), pd.Series(sx, index=idx))


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    n = int(p["swing_len"])
    c = bars_df["close"]
    long_f = (c - bars_df["low"].rolling(n).min()) / c
    short_f = (bars_df["high"].rolling(n).max() - c) / c
    le, _, se, _ = simulate(bars_df, **params)
    frac = long_f.where(le, short_f.where(se))         # the signal bar's own side
    return {"sl_stop": frac.shift(1)}                  # read on the fill bar


def portfolio_kwargs(**params):
    return {"upon_opposite_entry": "ignore"}
