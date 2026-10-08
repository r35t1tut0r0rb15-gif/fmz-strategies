"""Double EMA + range-change filter (MyLanguage): with the previous close above EMA(1000) of closes,
EMA 1000 above its EMA 100, and the up / down range-change balance positive and above its own
smoothing, reverse to long on the next bar; the mirror reverses to short. A long is taken off when
the close falls back under EMA 1000 more than 1 % above its entry (shorts mirrored).
Port of FMZ strategy #425797 "Trade03-双均线波动率差过滤".

Source
    https://www.fmz.com/strategy/425797 (MyLanguage, author 作手君TradeMan, FMZ last modified
    2023-09-04 22:33:22). Verbatim copy: original_source.md. Read 2026-10-07.

Original signal (original_source.md lines 44-75), S1 100, S2 = 10 S1, ST 1 %
    MA1 = EMA(REF(C,1), S2); MA2 = EMA(MA1, S1)
    DBF = H+L <= H1+L1 ? 0 : max(|H-H1|, |L-L1|);  KBF mirrors
    DBL = (DBF+S1) / ((DBF+S1)+(KBF+S1)); KBL likewise; CHANGE = DBL - KBL
    MACHANGE = MA(CHANGE, S1); MACHANGE2 = EMA(MACHANGE, S1)
    BUYK = BARPOS > S2 and C1 > MA1 > MA2 and CHANGE > 0 and MACHANGE > MACHANGE2   (SELLK mirrors)
    SELLY = C1 < MA1 and C1 > BKPRICE * 1.01;  BUYY = C1 > MA1 and C1 < SKPRICE * 0.99
    BKVOL <= 0 and REF(BUYK,1) -> BPK;  SKVOL <= 0 and REF(SELLK,1) -> SPK
    BKVOL > 0 and REF(SELLY,1) -> SP;  SKVOL > 0 and REF(BUYY,1) -> BP

Interpretation choices (MyLanguage rules in SURVEY_README.md)
    * Criterion 2: S1 is both a length and an additive constant in DBL / KBL, where it is in price
      units. The additive one becomes s1_atr x ATR(14); the lengths stay S1 / 10 S1.
    * BKPRICE / SKPRICE = the close of the BPK / SPK signal bar. Statements run in order on the
      completed bar; the port emits the bar's net position change.
    * BPK / SPK reverse an opposite position: REVERSAL INTENDED.
    * FREQ = "1h" from the backtest header. LOTS (MONEYTOT formula) -> original_sizing.txt.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_425797_ema_range_change_filter"
FAMILY = "ma_trend"  # proposed 2026-10-07, user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None
ATR_LEN = 14  # criterion 2 conversion length (fixed)

GRID = {
    "S1": [50, 100],
    "s1_atr": [0.25, 0.5, 1.0],
}
DEFAULT_PARAMS = {"S1": 100, "s1_atr": 0.5, "ST": 1.0}


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


def _atr_pine(bars, n):
    """ta.atr: Wilder RMA of the true range; the first bar's range is high - low (ta.tr(true))."""
    prev_close = bars["close"].shift(1)
    tr = pd.concat([bars["high"] - bars["low"],
                    (bars["high"] - prev_close).abs(),
                    (bars["low"] - prev_close).abs()], axis=1).max(axis=1)
    return _rma(tr, n)


def precompute(raw_1m_df, symbol_key, **params):
    return _resample(raw_1m_df, FREQ)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    s1 = int(p["S1"])
    s2 = 10 * s1
    h, l, c = bars_df["high"], bars_df["low"], bars_df["close"]
    c1 = c.shift(1)
    ma1 = c1.ewm(span=s2, adjust=False).mean()
    ma2 = ma1.ewm(span=s1, adjust=False).mean()
    h1, l1 = h.shift(1), l.shift(1)
    big = np.maximum((h - h1).abs(), (l - l1).abs())
    dbf = big.where(~((h + l) <= (h1 + l1)), 0.0)
    kbf = big.where(~((h + l) >= (h1 + l1)), 0.0)
    add = p["s1_atr"] * _atr_pine(bars_df, ATR_LEN)
    dbl = (dbf + add) / ((dbf + add) + (kbf + add))
    kbl = (kbf + add) / ((kbf + add) + (dbf + add))
    chg = dbl - kbl
    mac = chg.rolling(s1).mean()
    mac2 = mac.ewm(span=s1, adjust=False).mean()
    barpos = np.arange(1, len(c) + 1)
    buyk = ((barpos > s2) & (c1 > ma1) & (ma1 > ma2) & (chg > 0) & (mac > mac2)).to_numpy()
    sellk = ((barpos > s2) & (c1 < ma1) & (ma1 < ma2) & (chg < 0) & (mac < mac2)).to_numpy()
    lag = lambda a: np.concatenate([[False], a[:-1]])
    buyk1, sellk1 = lag(buyk), lag(sellk)
    cv, c1v, ma1v = c.to_numpy(dtype=float), c1.to_numpy(), ma1.to_numpy()
    st = 0.01 * p["ST"]
    m = len(cv)
    le, lx, se, sx = (np.zeros(m, dtype=bool) for _ in range(4))
    pos, bkp, skp = 0, np.nan, np.nan
    selly_prev = buyy_prev = False
    for i in range(m):
        before = pos
        if pos <= 0 and buyk1[i]:
            pos, bkp = 1, cv[i]
        if pos >= 0 and sellk1[i] and before != -1:
            pos, skp = -1, cv[i]
        if pos == 1 and selly_prev and before == 1:
            pos = 0
        if pos == -1 and buyy_prev and before == -1:
            pos = 0
        selly_prev = c1v[i] < ma1v[i] and c1v[i] > bkp * (1 + st)
        buyy_prev = c1v[i] > ma1v[i] and c1v[i] < skp * (1 - st)
        if pos != before:
            if pos == 1:
                le[i] = True
            elif pos == -1:
                se[i] = True
            elif before == 1:
                lx[i] = True
            else:
                sx[i] = True
    idx = bars_df.index
    return tuple(pd.Series(x, index=idx) for x in (le, lx, se, sx))


def portfolio_kwargs(**params):
    return {}
