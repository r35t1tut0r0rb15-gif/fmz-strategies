"""Trend bounces (racer8), 45-minute bars: above the SMA 200, a close under the previous 7-bar low goes long and a close
over the previous 7-bar high closes it; below the SMA 200 the mirror trades shorts; a stop 2 ATR (SMA of the true range,
10) from the entry fill guards each position.
Port of FMZ strategy #431903 "Long Term Trend Reversal Strategy" (Trend Bounce).

FMZ source id: 431903

Source
    https://www.fmz.com/strategy/431903 (PineScript v4, FMZ last modified 2023-11-13 10:51:35).
    Verbatim copy: original_source.md. Read 2026-10-17 (FMZ-C).

Original signal (original_source.md lines 211-252), channel 7, SMA 200, ATR stop 2 x sma(tr, 10)[1]
    close > sma200 and close < lowest(7)[1] -> entry long;  close > highest(7)[1] -> close long
    close < sma200 and close > highest(7)[1] -> entry short;  close < lowest(7)[1] -> close short
    stop = fill price -+ 2 x sma(tr, 10)[1] at the fill bar, kept (valuewhen(bought))

Interpretation choices (Pine rules in SURVEY_README.md)
    * The stop is fixed at the fill: 2 x the ATR known at the fill bar's open (the SMA of the true
      range up to the signal bar), ported as a fraction of the signal close, shifted one bar (re-based
      on the fill; vbt applies it from the fill bar, the source one bar later, as #365892).
    * Order of the source: entry long, close long, entry short, close short; a close acts on the
      position held at the bar's start and does not undo a reversal. "Flat" follows the house stop on
      bars. strategy.entry reverses: REVERSAL INTENDED. Stop module: portfolio_kwargs {} (driver D4).
      FREQ = "45min" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; stop fixed at the fill.
    2 generic: PASS, Donchian levels, an SMA and ATR multiples.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_431903_trend_bounce_channel"
FAMILY = "donchian_breakout"  # proposed 2026-10-17 (FMZ-C), user to confirm
FREQ = "45min"  # backtest header period: 45m
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "nn": [7, 14],
    "slm": [2.0, 3.0],
}
DEFAULT_PARAMS = {"nn": 7, "ma_len": 200, "slm": 2.0}


def _resample(raw_1m_df, freq):
    ohlc = raw_1m_df[["open", "high", "low", "close"]]
    bars = ohlc.resample(freq, label="left", closed="left").agg(
        {"open": "first", "high": "max", "low": "min", "close": "last"})
    bars = bars.dropna(how="all")  # an empty period is not a bar; never forward-filled
    if bars.index.tz is None:
        raise ValueError("raw_1m_df must have a tz-aware UTC index")
    return bars


def _run(bars_df, p):
    o, h, lo, c = (bars_df[k] for k in ("open", "high", "low", "close"))
    n = int(p["nn"])
    hi1 = h.rolling(n).max().shift(1).to_numpy()
    lo1 = lo.rolling(n).min().shift(1).to_numpy()
    ma = c.rolling(int(p["ma_len"])).mean().to_numpy()
    c1 = c.shift(1)
    tr = pd.concat([h - lo, (h - c1).abs(), (lo - c1).abs()], axis=1).max(axis=1)
    atr_s = tr.rolling(10).mean().to_numpy()                  # sma(tr, 10) of the signal bar = [1] at the fill
    ov, hv, lv, cv = (x.to_numpy(dtype=float) for x in (o, h, lo, c))
    slm = float(p["slm"])
    m = len(cv)
    tgt = np.zeros(m, dtype=np.int8)
    sl_f = np.full(m, np.nan)
    pos, e_i, s_ = 0, -1, np.nan
    for i in range(m):
        if pos != 0 and i >= e_i and i < m and not np.isnan(s_):   # house stop from the fill price
            e = ov[e_i]
            if (pos == 1 and lv[i] <= e * (1 - s_)) or (pos == -1 and hv[i] >= e * (1 + s_)):
                pos = 0
        start = pos
        if cv[i] > ma[i] and cv[i] < lo1[i]:
            pos = 1
        if start == 1 and pos == 1 and cv[i] > hi1[i]:
            pos = 0
        if cv[i] < ma[i] and cv[i] > hi1[i]:
            pos = -1
        if start == -1 and pos == -1 and cv[i] < lo1[i]:
            pos = 0
        if pos != start and pos != 0:
            e_i = i + 1
            s_ = slm * atr_s[i] / cv[i]
            sl_f[i] = s_
        tgt[i] = pos
    return tgt, sl_f


def _emit(tgt, index):
    prev = np.concatenate(([0], tgt[:-1]))
    le = (tgt == 1) & (prev != 1)
    lx = (prev == 1) & (tgt == 0)
    se = (tgt == -1) & (prev != -1)
    sx = (prev == -1) & (tgt == 0)
    return tuple(pd.Series(a, index=index) for a in (le, lx, se, sx))


def precompute(raw_1m_df, symbol_key, **params):
    return _resample(raw_1m_df, FREQ)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    tgt, _ = _run(bars_df, p)
    return _emit(tgt, bars_df.index)


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    _, sl_f = _run(bars_df, p)
    return {"sl_stop": pd.Series(sl_f, index=bars_df.index).shift(1)}


def portfolio_kwargs(**params):
    return {}
