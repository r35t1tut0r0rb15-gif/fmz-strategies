"""EMA trend filter + KD (stochastic) pullback entry, close stop and MA-break profit exit.
Port of FMZ strategy #128249 "传统均线指标与KD指标的交易策略" (traditional MA and KD strategy).

Source
    https://www.fmz.com/strategy/128249 (MyLanguage, author "阿基米德的浴缸", FMZ last modified
    2019-08-20 10:30:47). Verbatim copy: original_source.md. Read 2026-10-07.

Original signal (original_source.md lines 69-89), SLOSS 2, N 120
    MAC = EMA(C,N); RSV = (C-LLV(L,9))/(HHV(H,9)-LLV(L,9))*100; K = SMA(RSV,3,1); D = SMA(K,3,1)
    BARPOS>N AND C>MAC AND K<D -> BK;   BARPOS>N AND C<MAC AND K>D -> SK
    C <= BKPRICE*(1-SLOSS%) -> SP;      C >= SKPRICE*(1+SLOSS%) -> BP
    C >= BKPRICE*(1+SLOSS%) AND C<MAC -> SP;   C <= SKPRICE*(1-SLOSS%) AND C>MAC -> BP
    (no AUTOFILTER)

Interpretation choices (MyLanguage rules in SURVEY_README.md)
    * Close-price model, completed bars, one signal per bar in source order.
    * No AUTOFILTER: a BK bar while long is an add (sizing, not ported) that moves BKPRICE to
      that bar's close and is that bar's signal, so the exits are not checked on it. A BK bar
      while short would open a second, opposite leg on FMZ; a net-position port cannot hold it,
      so it is ignored and the short's exits are checked as usual (mirror for SK).
      Opposite entries cannot occur; portfolio_kwargs also returns upon_opposite_entry="ignore".
    * Criterion 2: SLOSS % becomes `sl_atr` x Wilder ATR(14) on the BKPRICE/SKPRICE bar, for both
      the stop and the profit-exit threshold.
    * A 9-bar range of zero makes RSV undefined; such bars give no K/D signal.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_128249_ema_kd_pullback"
FAMILY = "ma_trend_oscillator_pullback"  # proposed 2026-10-07, user to confirm
FREQ = "30min"  # backtest header period: 30m
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "n": [60, 120, 240],
    "nkd": [5, 9, 14],
    "sl_atr": [1.0, 2.0, 3.0],
}
DEFAULT_PARAMS = {"n": 120, "nkd": 9, "m1": 3, "m2": 3, "sl_atr": 2.0, "atr_length": 14}


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


def _atr(bars, n):
    prev_close = bars["close"].shift(1)
    tr = pd.concat([bars["high"] - bars["low"],
                    (bars["high"] - prev_close).abs(),
                    (bars["low"] - prev_close).abs()], axis=1).max(axis=1, skipna=False)
    return _rma(tr, n)


def precompute(raw_1m_df, symbol_key, **params):
    return _resample(raw_1m_df, FREQ)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    n, nkd = int(p["n"]), int(p["nkd"])
    high, low, close = bars_df["high"], bars_df["low"], bars_df["close"]
    mac = close.ewm(span=n, adjust=False).mean()
    hh, ll = high.rolling(nkd).max(), low.rolling(nkd).min()
    rsv = ((close - ll) / (hh - ll) * 100).replace([np.inf, -np.inf], np.nan)
    k = rsv.ewm(alpha=1 / p["m1"], adjust=False, ignore_na=True).mean()   # SMA(RSV,3,1)
    d = k.ewm(alpha=1 / p["m2"], adjust=False, ignore_na=True).mean()     # SMA(K,3,1)
    warm = np.arange(len(close)) + 1 > n                                  # BARPOS > N
    bk = (warm & (close > mac) & (k < d) & rsv.notna()).to_numpy()
    sk = (warm & (close < mac) & (k > d) & rsv.notna()).to_numpy()
    atr = _atr(bars_df, int(p["atr_length"])).to_numpy()
    c, macv = close.to_numpy(), mac.to_numpy()

    m = len(c)
    le, lx, se, sx = (np.zeros(m, dtype=bool) for _ in range(4))
    pos, ref, dist = 0, np.nan, np.nan
    for i in range(m):
        if np.isnan(atr[i]):
            continue
        if bk[i] and pos >= 0:            # BK: open from flat, or add while long
            if pos == 0:
                le[i] = True
            pos, ref, dist = 1, c[i], p["sl_atr"] * atr[i]
            continue
        if sk[i] and pos <= 0:
            if pos == 0:
                se[i] = True
            pos, ref, dist = -1, c[i], p["sl_atr"] * atr[i]
            continue
        if pos == 1 and (c[i] <= ref - dist or (c[i] >= ref + dist and c[i] < macv[i])):
            lx[i], pos = True, 0
        elif pos == -1 and (c[i] >= ref + dist or (c[i] <= ref - dist and c[i] > macv[i])):
            sx[i], pos = True, 0

    idx = bars_df.index
    return (pd.Series(le, index=idx), pd.Series(lx, index=idx),
            pd.Series(se, index=idx), pd.Series(sx, index=idx))


def portfolio_kwargs(**params):
    return {"upon_opposite_entry": "ignore"}
