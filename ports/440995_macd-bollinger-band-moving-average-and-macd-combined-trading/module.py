"""EMA 34 against the Bollinger basis 150 with MACD (9, 17, 9) confirmation, 2-hour bars: the EMA above the basis with MACD above its signal and the signal above zero goes long, the mirror goes short,
once per side until reset; a fixed tick bracket (about 29.2 ATR target, 17.8 ATR stop); the EMA and MACD turning against the position close it.
Port of FMZ strategy #440995 "基于布林带移动平均线和MACD的组合交易策略Bollinger-Band-Moving-Average-and-MACD-Combined-Trading-Strategy" (Comb Strat).

FMZ source id: 440995

Source
    https://www.fmz.com/strategy/440995 (PineScript v5, FMZ last modified 2024-02-04 15:42:23).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 178-261), BB 150 / 2 on close; EMA 34 (smoothing line plotted only); MACD 9 / 17, signal 9, EMAs; takeProfitTicks 87636, stopLossTicks 53350; 10 % of equity
    long = ema34 > basis and macd > signal and signal > 0;  short = ema34 < basis and macd < signal and signal < 0
    long and not longExecuted -> entry Long, longExecuted = true, shortExecuted = na;  short and not shortExecuted -> entry Short, shortExecuted = true, longExecuted = na
    strategy.exit(profit = 87636, loss = 53350) for each side;  ema < basis and macd < signal -> close Long, longExecuted = na;  ema > basis and macd > signal -> close Short, shortExecuted = na

Interpretation choices (Pine rules in SURVEY_README.md)
    * The bracket is a fixed count of ticks, 8763.6 and 5335 price units at mintick 0.1 on the BTC
      reading: as ATR multiples at the 2-hour ATR(14) reading of about 300, a target of 29.2 ATR and a stop
      of 17.8 ATR, taken from the signal bar (sl / tp = k ATR / close, shifted one bar inside stops()). The
      executed flags keep one entry per side until the close condition for that side resets it (a stop exit
      leaves the flag set). An entry signal reverses the opposite position, and the close of that position
      written after it leaves the reversal standing (as #438020). The smoothing line and the histogram are
      plotted only. The 10 % of equity size is sizing. REVERSAL INTENDED. Stop module: portfolio_kwargs {}
      (driver D4). Stops on 2-hour bars: mark coarse_bar_stop. FREQ = "2h" from the backtest header (bars on
      UTC multiples of 2 hours).

Admission criteria
    1 fits the interface: PASS, bar-close orders; bracket fixed at entry.
    2 generic: ADAPT, fixed tick bracket -> ATR multiples.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: the percent-of-equity size stored.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
REVERSAL INTENDED.

Marks: coarse_bar_stop
"""
import numpy as np
import pandas as pd

NAME = "fmz_440995_ema34_bb150_macd_once_per_side_bracket"
FAMILY = "multi_indicator_confluence"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "2h"  # backtest header period: 2h
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "bb_len": [150, 75],
    "ema_len": [34, 17],
}
DEFAULT_PARAMS = {"bb_len": 150, "ema_len": 34, "fast": 9, "slow": 17, "signal": 9,
                  "atr_len": 14, "tp_atr": 29.2, "sl_atr": 17.8}


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


def _fractions(bars_df, p):
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    pc = c.shift(1)
    tr = pd.concat([h - lo, (h - pc).abs(), (lo - pc).abs()], axis=1).max(axis=1)
    a = _rma(tr, int(p["atr_len"])) / c
    return float(p["sl_atr"]) * a, float(p["tp_atr"]) * a


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    c = bars_df["close"]
    basis = c.rolling(int(p["bb_len"])).mean()
    e = c.ewm(span=int(p["ema_len"]), adjust=False).mean()
    macd = c.ewm(span=int(p["fast"]), adjust=False).mean() - c.ewm(span=int(p["slow"]), adjust=False).mean()
    sig = macd.ewm(span=int(p["signal"]), adjust=False).mean()
    lc = ((e > basis) & (macd > sig) & (sig > 0)).to_numpy()
    sc = ((e < basis) & (macd < sig) & (sig < 0)).to_numpy()
    cl = ((e < basis) & (macd < sig)).to_numpy()
    cs = ((e > basis) & (macd > sig)).to_numpy()
    sl_s, tp_s = _fractions(bars_df, p)
    sl, tp = sl_s.to_numpy(), tp_s.to_numpy()
    ov = bars_df["open"].to_numpy(dtype=float)
    hv, lv = bars_df["high"].to_numpy(dtype=float), bars_df["low"].to_numpy(dtype=float)
    m = len(ov)
    le, lx = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    se, sx = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    pos, entry_i, s_, t_ = 0, -1, np.nan, np.nan
    lf, sf = False, False
    for i in range(m):
        if pos != 0 and i >= entry_i:
            x = ov[entry_i]
            if pos == 1 and (lv[i] <= x * (1 - s_) or hv[i] >= x * (1 + t_)):
                pos = 0
            elif pos == -1 and (hv[i] >= x * (1 + s_) or lv[i] <= x * (1 - t_)):
                pos = 0
        entered = False
        if lc[i] and not lf and i + 1 < m and not np.isnan(sl[i]):
            if pos != 1:
                le[i], pos, entry_i, s_, t_, entered = True, 1, i + 1, sl[i], tp[i], True
            lf, sf = True, False
        if sc[i] and not sf and i + 1 < m and not np.isnan(sl[i]):
            if pos != -1:
                se[i], pos, entry_i, s_, t_, entered = True, -1, i + 1, sl[i], tp[i], True
            sf, lf = True, False
        if cl[i]:
            if pos == 1 and not entered and i >= entry_i:
                lx[i], pos = True, 0
            lf = False
        if cs[i]:
            if pos == -1 and not entered and i >= entry_i:
                sx[i], pos = True, 0
            sf = False
    ix = bars_df.index
    return (pd.Series(le, index=ix), pd.Series(lx, index=ix),
            pd.Series(se, index=ix), pd.Series(sx, index=ix))


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    sl, tp = _fractions(bars_df, p)
    return {"sl_stop": sl.shift(1), "tp_stop": tp.shift(1)}


def portfolio_kwargs(**params):
    return {}
