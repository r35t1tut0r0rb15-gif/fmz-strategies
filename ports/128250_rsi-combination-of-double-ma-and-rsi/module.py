"""Dual-EMA trend + RSI momentum cross entry; close stop and MA-flip profit exit.
Port of FMZ strategy #128250 "双均线策略与相对强弱RSI指标组合" (double MA and RSI).

Source
    https://www.fmz.com/strategy/128250 (MyLanguage, author "阿基米德的浴缸", FMZ last modified
    2019-08-20 10:29:50). Verbatim copy: original_source.md. Read 2026-10-07.

Original signal (original_source.md lines 70-89), SLOSS true (=1), N1 50, N2 300
    MA1 = EMA(C,N1); MA2 = EMA(C,N2)
    RSI = SMA(MAX(C-REF(C,1),0),9,1) / SMA(ABS(C-REF(C,1)),9,1) * 100
    BUYK  = BKVOL=0 AND BARPOS>N2 AND MA1>MA2 AND C>MAX(MA1,MA2) AND CROSSUP(RSI,70)   -> BK
    SELLK = SKVOL=0 AND BARPOS>N2 AND MA1<MA2 AND C<MIN(MA1,MA2) AND CROSSDOWN(RSI,30) -> SK
    SELLY = MA1<MA2 AND C>BKPRICE*(1+SLOSS%) -> SP;   BUYY = MA1>MA2 AND C<SKPRICE*(1-SLOSS%) -> BP
    SELLS = C<BKPRICE*(1-SLOSS%) -> SP;               BUYS = C>SKPRICE*(1+SLOSS%) -> BP

Interpretation choices (MyLanguage rules in SURVEY_README.md)
    * Close-price model, completed bars, one signal per bar in source order.
    * SLOSS is given as `true` in the argument table, i.e. 1 (%).
    * BUYK requires BKVOL=0 but not SKVOL=0: on FMZ a BK while short opens a second, hedged leg.
      The net-position port ignores it and keeps checking the short's exits (mirror for SK).
      Opposite entries cannot occur; portfolio_kwargs also returns upon_opposite_entry="ignore".
    * Criterion 2: SLOSS % becomes `sl_atr` x Wilder ATR(14) of the entry signal bar, for both the
      stop and the profit threshold. Both are close conditions -> exit signals.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_128250_dual_ema_rsi_momentum"
FAMILY = "ma_trend"  # proposed 2026-10-07, user to confirm
FREQ = "15min"  # backtest header period: 15m
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "n1": [20, 50, 100],
    "n2": [150, 300, 450],
    "sl_atr": [1.0, 2.0, 3.0],
}
DEFAULT_PARAMS = {"n1": 50, "n2": 300, "rsi_length": 9, "overbought": 70, "sl_atr": 2.0, "atr_length": 14}


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
    close = bars_df["close"]
    ma1 = close.ewm(span=int(p["n1"]), adjust=False).mean()
    ma2 = close.ewm(span=int(p["n2"]), adjust=False).mean()
    dc = close.diff()
    a = 1 / p["rsi_length"]
    rsi = (dc.clip(lower=0).ewm(alpha=a, adjust=False, ignore_na=True).mean()
           / dc.abs().ewm(alpha=a, adjust=False, ignore_na=True).mean() * 100)
    ob, osold = p["overbought"], 100 - p["overbought"]
    warm = np.arange(len(close)) + 1 > int(p["n2"])                       # BARPOS > N2
    buyk = (warm & (ma1 > ma2) & (close > np.maximum(ma1, ma2))
            & (rsi > ob) & (rsi.shift(1) <= ob)).to_numpy()
    sellk = (warm & (ma1 < ma2) & (close < np.minimum(ma1, ma2))
             & (rsi < osold) & (rsi.shift(1) >= osold)).to_numpy()
    up = (ma1 > ma2).to_numpy()
    dn = (ma1 < ma2).to_numpy()
    atr = _atr(bars_df, int(p["atr_length"])).to_numpy()
    c = close.to_numpy()

    m = len(c)
    le, lx, se, sx = (np.zeros(m, dtype=bool) for _ in range(4))
    pos, ref, dist = 0, np.nan, np.nan
    for i in range(m):
        if pos == 0 and not np.isnan(atr[i]):
            if buyk[i]:
                le[i], pos, ref, dist = True, 1, c[i], p["sl_atr"] * atr[i]
            elif sellk[i]:
                se[i], pos, ref, dist = True, -1, c[i], p["sl_atr"] * atr[i]
        elif pos == 1 and ((dn[i] and c[i] > ref + dist) or c[i] < ref - dist):
            lx[i], pos = True, 0
        elif pos == -1 and ((up[i] and c[i] < ref - dist) or c[i] > ref + dist):
            sx[i], pos = True, 0

    idx = bars_df.index
    return (pd.Series(le, index=idx), pd.Series(lx, index=idx),
            pd.Series(se, index=idx), pd.Series(sx, index=idx))


def portfolio_kwargs(**params):
    return {"upon_opposite_entry": "ignore"}
