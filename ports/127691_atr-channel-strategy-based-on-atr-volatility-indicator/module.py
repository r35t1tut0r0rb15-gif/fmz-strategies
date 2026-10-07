"""N-bar high/low stop-and-reverse with an ATR-band profit exit and a close-based stop.
Port of FMZ strategy #127691 "基于ATR波动率指标构建的通道策略" (channel strategy based on ATR).

Source
    https://www.fmz.com/strategy/127691 (MyLanguage, author "Zero", FMZ last modified
    2018-12-21 16:13:58). Verbatim copy: original_source.md. Read 2026-10-07.

Original signal (original_source.md lines 50-67), SLOSS 2, N 200, M 4
    ATR = MA(TR,N); MAC = MA(C,N); UBAND = MAC + M*ATR; DBAND = MAC - M*ATR
    H >= HHV(H,N) -> BPK;   L <= LLV(L,N) -> SPK
    (H >= HHV(H,M*N) OR C <= UBAND) AND BKHIGH >= BKPRICE*(1+M*SLOSS%) -> SP
    (L <= LLV(L,M*N) OR C >= DBAND) AND SKLOW  <= SKPRICE*(1-M*SLOSS%) -> BP
    C >= SKPRICE*(1+SLOSS%) -> BP;   C <= BKPRICE*(1-SLOSS%) -> SP
    AUTOFILTER

Interpretation choices (MyLanguage rules in SURVEY_README.md)
    * Close-price model, completed bars. HHV/LLV include the current bar, so "H >= HHV(H,N)"
      is "this bar made the N-bar high".
    * AUTOFILTER: one signal per bar, first valid statement in source order. BPK while flat
      opens long; while short it reverses. REVERSAL INTENDED (portfolio_kwargs {}; the engine's
      default opposite-entry reversal applies). BPK while already long is not a signal.
    * BKPRICE = the entry signal bar's close; BKHIGH = highest high of the bars after it, up to
      and including the current bar.
    * Criterion 2: SLOSS % becomes `sl_atr` x the source's own ATR (MA of TR over N) on the
      entry signal bar; the profit-exit activation M*SLOSS % becomes M x that distance, keeping
      the source's M coupling. Both stops/targets are close/bar conditions -> exit signals.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_127691_atr_channel_stop_and_reverse"
FAMILY = "donchian_breakout"  # proposed 2026-10-07, user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "n": [100, 200, 300],
    "m": [2, 3, 4],
    "sl_atr": [1.0, 2.0, 3.0],
}
DEFAULT_PARAMS = {"n": 200, "m": 4, "sl_atr": 2.0}


def _resample(raw_1m_df, freq):
    ohlc = raw_1m_df[["open", "high", "low", "close"]]
    bars = ohlc.resample(freq, label="left", closed="left").agg(
        {"open": "first", "high": "max", "low": "min", "close": "last"})
    bars = bars.dropna(how="all")  # an empty period is not a bar; never forward-filled
    if bars.index.tz is None:
        raise ValueError("raw_1m_df must have a tz-aware UTC index")
    return bars


def _true_range(bars):
    prev_close = bars["close"].shift(1)
    return pd.concat([bars["high"] - bars["low"],
                      (prev_close - bars["high"]).abs(),
                      (prev_close - bars["low"]).abs()], axis=1).max(axis=1, skipna=False)


def precompute(raw_1m_df, symbol_key, **params):
    return _resample(raw_1m_df, FREQ)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    n, mm = int(p["n"]), p["m"]
    high, low, close = bars_df["high"], bars_df["low"], bars_df["close"]
    atr = _true_range(bars_df).rolling(n).mean()
    mac = close.rolling(n).mean()
    uband = (mac + mm * atr).to_numpy()
    dband = (mac - mm * atr).to_numpy()
    nh = high.rolling(n).max().to_numpy()
    nl = low.rolling(n).min().to_numpy()
    nh_long = high.rolling(int(mm * n)).max().to_numpy()
    nl_long = low.rolling(int(mm * n)).min().to_numpy()
    atr = atr.to_numpy()
    c, h, lo = close.to_numpy(), high.to_numpy(), low.to_numpy()

    m = len(c)
    le, lx, se, sx = (np.zeros(m, dtype=bool) for _ in range(4))
    pos, ref, dist, ext = 0, np.nan, np.nan, np.nan
    for i in range(m):
        if pos == 1:
            ext = max(ext, h[i])
        elif pos == -1:
            ext = min(ext, lo[i])
        ok = not np.isnan(atr[i])
        if ok and pos != 1 and h[i] >= nh[i]:                       # BPK
            le[i], pos, ref, dist, ext = True, 1, c[i], p["sl_atr"] * atr[i], -np.inf
        elif ok and pos != -1 and lo[i] <= nl[i]:                   # SPK
            se[i], pos, ref, dist, ext = True, -1, c[i], p["sl_atr"] * atr[i], np.inf
        elif pos == 1 and (h[i] >= nh_long[i] or c[i] <= uband[i]) and ext >= ref + mm * dist:
            lx[i], pos = True, 0                                    # SP (profit exit)
        elif pos == -1 and (lo[i] <= nl_long[i] or c[i] >= dband[i]) and ext <= ref - mm * dist:
            sx[i], pos = True, 0                                    # BP (profit exit)
        elif pos == -1 and c[i] >= ref + dist:
            sx[i], pos = True, 0                                    # BP (stop)
        elif pos == 1 and c[i] <= ref - dist:
            lx[i], pos = True, 0                                    # SP (stop)

    idx = bars_df.index
    return (pd.Series(le, index=idx), pd.Series(lx, index=idx),
            pd.Series(se, index=idx), pd.Series(sx, index=idx))


def portfolio_kwargs(**params):
    return {}
