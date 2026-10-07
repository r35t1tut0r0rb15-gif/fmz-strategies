"""MACD + dual-SMA trend entry, exit on MACD sign / MA order flip or a low-touch stop.
Port of FMZ strategy #127101 "你不知道的MACDMA指标组合策略" (MACD-MA indicator combination).

Source
    https://www.fmz.com/strategy/127101 (MyLanguage, author "Zero", FMZ last modified
    2018-12-14 10:25:27). Verbatim copy: original_source.md. Read 2026-10-07.

Original signal (original_source.md lines 34-70)
    MACD = EMA(C,12)-EMA(C,26); AVG = EMA(MACD,9); DIFF = MACD-AVG; DMA1 = MA(C,50); DMA2 = MA(C,120)
    BUY  = MACD>0 && DMA1>DMA2 && DIFF>0 && C>DMA1 && REF(C,1)>REF(DMA1,1)
    SELL = MACD<0 && DMA1<DMA2 && DIFF<0 && C<DMA1 && REF(C,1)<REF(DMA1,1)
    BKVOL=0 AND BUY -> BK;  SKVOL=0 AND SELL -> SK
    long:  REF(MACD,1)<0 OR REF(DMA1,1)<REF(DMA2,1) -> SP;  LOW <= BKPRICE*(1-5%) -> SP
    short: REF(MACD,1)>0 OR REF(DMA1,1)>REF(DMA2,1) -> BP;  HIGH >= SKPRICE*(1+5%) -> BP
    AUTOFILTER

Interpretation choices (MyLanguage rules in SURVEY_README.md)
    * Close-price model: every rule on the completed bar; BKPRICE = the entry signal bar's close.
    * The 5 % stop is a condition on the completed bar's low/high, so it is an exit signal here,
      not sl_stop. Criterion 2: 5 % becomes `stop_atr` x Wilder ATR(14) of the entry signal bar.
    * AUTOFILTER: entries only from flat, one signal per bar (an exit bar emits no entry).
      Opposite entries cannot occur; portfolio_kwargs also returns upon_opposite_entry="ignore".
    * SETSIGPRICETYPE(.., NEW_ORDER) is order-price execution: original_sizing.txt.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_127101_macd_dual_sma_trend"
FAMILY = "ma_trend"  # proposed 2026-10-07, user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "ma_fast": [30, 50, 80],
    "ma_slow": [100, 120, 200],
    "stop_atr": [3.0, 6.0, 9.0],
}
DEFAULT_PARAMS = {"ma_fast": 50, "ma_slow": 120, "stop_atr": 6.0, "macd_fast": 12,
                  "macd_slow": 26, "macd_signal": 9, "atr_length": 14}


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


def _ema(x, n):
    return x.ewm(span=n, adjust=False).mean()


def precompute(raw_1m_df, symbol_key, **params):
    return _resample(raw_1m_df, FREQ)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    close = bars_df["close"]
    macd = _ema(close, int(p["macd_fast"])) - _ema(close, int(p["macd_slow"]))
    diff = macd - _ema(macd, int(p["macd_signal"]))
    ma1 = close.rolling(int(p["ma_fast"])).mean()
    ma2 = close.rolling(int(p["ma_slow"])).mean()
    buy = ((macd > 0) & (ma1 > ma2) & (diff > 0) & (close > ma1) & (close.shift(1) > ma1.shift(1))).to_numpy()
    sell = ((macd < 0) & (ma1 < ma2) & (diff < 0) & (close < ma1) & (close.shift(1) < ma1.shift(1))).to_numpy()
    long_out = ((macd.shift(1) < 0) | (ma1.shift(1) < ma2.shift(1))).to_numpy()
    short_out = ((macd.shift(1) > 0) | (ma1.shift(1) > ma2.shift(1))).to_numpy()
    atr = _atr(bars_df, int(p["atr_length"])).to_numpy()
    c, h, lo = (bars_df[k].to_numpy(dtype=float) for k in ("close", "high", "low"))

    m = len(c)
    le, lx, se, sx = (np.zeros(m, dtype=bool) for _ in range(4))
    pos, stop_level = 0, np.nan
    for i in range(m):
        if pos == 1:
            if long_out[i] or lo[i] <= stop_level:
                lx[i], pos = True, 0
        elif pos == -1:
            if short_out[i] or h[i] >= stop_level:
                sx[i], pos = True, 0
        elif not np.isnan(atr[i]):
            if buy[i]:
                le[i], pos, stop_level = True, 1, c[i] - p["stop_atr"] * atr[i]
            elif sell[i]:
                se[i], pos, stop_level = True, -1, c[i] + p["stop_atr"] * atr[i]

    idx = bars_df.index
    return (pd.Series(le, index=idx), pd.Series(lx, index=idx),
            pd.Series(se, index=idx), pd.Series(sx, index=idx))


def portfolio_kwargs(**params):
    return {"upon_opposite_entry": "ignore"}
