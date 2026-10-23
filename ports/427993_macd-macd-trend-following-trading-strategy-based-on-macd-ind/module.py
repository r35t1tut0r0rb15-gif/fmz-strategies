"""A slow EMA 144 / 312 / 108 MACD histogram rising (falling) against its value 1-30 bars back, with the histogram 50 bars ago below (above) zero, a stochastic D under 20 (over 80), rising volume and a blended multi-length stochastic trend, 10-minute bars, re-armed by flags: the rising set goes long, the falling set goes short; the stochastic D over 80 (under 20), a close 4 % against the entry, a 10 % close in profit or the blended stochastic crossing 20 (80) closes; reversing.
Port of FMZ strategy #427993 "基于MACD指标的趋势跟踪交易策略MACD-Trend-Following-Trading-Strategy-Based-on-MACD-Indicator" (自用策略v0.2 (MACD trend following)).

FMZ source id: 427993

Source
    https://www.fmz.com/strategy/427993 (PineScript v4, FMZ last modified 2023-09-27 16:46:38).
    Verbatim copy: original_source.md. Read 2026-10-23 (FMZ-C).

Original signal (original_source.md lines 213-320), stoch 14 / 42 / 126 / 378 (smoothing 1 / 3 / 9 / 27), D 3, blend SMA 30; MACD EMA 144 / 312 / 108; steps 30 / 20 / 10 / 5 / 3 / 1, hist step 50; SL 4 %, TP 10 % (close tests); strategy() commented out
    hist[50] < 0 and hist - hist[n] >= 0 for n = 30, 20, 10, 5, 3, 1 and d < 20 and volume > volume[1] and true2_1 == 1 and allp > allp[1] and allp < 80 -> entry long, true2_1 := 0
    d > 80 -> close long, true2_1 := 1;  close < avg x 0.96 or crossunder(allp, 20) -> close long, true2_1 := 1;  close > avg x 1.1 -> close long;  short mirror with true2_2 (its stop line compares true2_2 == 1, a no-op)

Interpretation choices (Pine rules in SURVEY_README.md)
    * The flags run as written: true2_1 (long re-arm) is set by an all-falling histogram, a D over 80 or
      the long stop test, and cleared by a long entry; true2_2 (short re-arm) is cleared by an all-rising
      histogram and set by a D under 20 (the short stop line only compares, as written). The stop / target
      tests use the average price of whatever position is open (a long test can fire on a short's price,
      changing only the flag). The closes act only on a position the bar's entries leave unchanged.
      REVERSAL INTENDED. strategy() is commented out (cash 10000 is sizing). FREQ = "10min" from the
      backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; close-based stop / target.
    2 generic: PASS, slow MACD histogram momentum with stochastic and volume filters.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: the commented strategy() (cash 10000, capital 10000) stored, not ported.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: used: the bars' volume column (broker tick volume of the cTrader M1 data, summed per bar) in volume > volume[1] on both entries; exchange volume to be compared later (Austin, 2026-10-23).
Session open: not used.
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_427993_slow_macd_hist_steps_stoch_blend_volume_flags_close_bracket_reversal"
FAMILY = "macd_momentum"  # proposed 2026-10-23 (FMZ-C), user to confirm
FREQ = "10min"  # backtest header period: 10m
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "stop_loss": [4.0, 2.0],
    "target": [10.0, 5.0],
}
DEFAULT_PARAMS = {"stop_loss": 4.0, "target": 10.0, "fast": 144, "slow": 312, "signal": 108}


def _resample(raw_1m_df, freq):
    ohlcv = raw_1m_df[["open", "high", "low", "close", "volume"]]
    bars = ohlcv.resample(freq, label="left", closed="left").agg(
        {"open": "first", "high": "max", "low": "min", "close": "last", "volume": "sum"})
    bars = bars.dropna(subset=["close"])  # an empty period is not a bar; never forward-filled
    if bars.index.tz is None:
        raise ValueError("raw_1m_df must have a tz-aware UTC index")
    return bars


def precompute(raw_1m_df, symbol_key, **params):
    return _resample(raw_1m_df, FREQ)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    o, h, lo, c, v = (bars_df[k] for k in ("open", "high", "low", "close", "volume"))

    def stoch(n):
        ll, hh = lo.rolling(n).min(), h.rolling(n).max()
        return 100 * (c - ll) / (hh - ll).replace(0.0, np.nan)

    k = stoch(14)
    k2, k3, k4 = stoch(42).rolling(3).mean(), stoch(126).rolling(9).mean(), stoch(378).rolling(27).mean()
    d = k.rolling(3).mean()
    allp = ((k + k2 * 3 + k3 * 9 + k4 * 18) / 31).rolling(30).mean()
    macd = c.ewm(span=int(p["fast"]), adjust=False).mean() - c.ewm(span=int(p["slow"]), adjust=False).mean()
    hist = macd - macd.ewm(span=int(p["signal"]), adjust=False).mean()
    chas = [hist - hist.shift(n) for n in (30, 20, 10, 5, 3, 1)]
    all_up = np.logical_and.reduce([(x >= 0).to_numpy() for x in chas])
    all_dn = np.logical_and.reduce([(x <= 0).to_numpy() for x in chas])
    hc = hist.shift(50).to_numpy()
    dv, av, av1 = d.to_numpy(), allp.to_numpy(), allp.shift(1).to_numpy()
    vup = (v > v.shift(1)).to_numpy()
    ov, cv = o.to_numpy(dtype=float), c.to_numpy(dtype=float)
    ksl, ktp = float(p["stop_loss"]) / 100, float(p["target"]) / 100
    m = len(cv)
    le, lx, se, sx = (np.zeros(m, dtype=bool) for _ in range(4))
    pos, avg = 0, np.nan
    t21 = t22 = 0
    for i in range(m):
        old = pos
        if all_up[i]:
            t22 = 0
        if all_dn[i]:
            t21 = 1
        lcond = hc[i] < 0 and all_up[i] and dv[i] < 20 and vup[i] and t21 == 1 and av[i] > av1[i] and av[i] < 80
        if lcond:
            t21 = 0
        lclose = False
        if dv[i] > 80:
            lclose, t21 = True, 1
        if cv[i] < avg * (1 - ksl) or (av[i] < 20 and av1[i] > 20):
            lclose, t21 = True, 1
        if cv[i] > avg * (1 + ktp):
            lclose = True
        scond = hc[i] > 0 and all_dn[i] and dv[i] > 80 and vup[i] and t22 == 1 and av[i] < av1[i] and av[i] > 20
        if scond:
            t22 = 0
        sclose = False
        if dv[i] < 20:
            sclose, t22 = True, 1
        if cv[i] > avg * (1 + ksl) or (av[i] > 80 and av1[i] < 80):
            sclose = True                                   # "true2_2 == 1" only compares, as written
        if cv[i] < avg * (1 - ktp):
            sclose = True
        tgt = old
        if lcond:
            tgt = 1
        if scond:
            tgt = -1
        if tgt == old == 1 and lclose:
            tgt = 0
        elif tgt == old == -1 and sclose:
            tgt = 0
        pos = tgt
        if pos != old and pos != 0 and i + 1 < m:
            avg = ov[i + 1]
        elif pos == 0:
            avg = np.nan
        if pos == 1 and old != 1:
            le[i] = True
        elif pos == -1 and old != -1:
            se[i] = True
        elif pos == 0 and old == 1:
            lx[i] = True
        elif pos == 0 and old == -1:
            sx[i] = True
    ix = bars_df.index
    return (pd.Series(le, index=ix), pd.Series(lx, index=ix),
            pd.Series(se, index=ix), pd.Series(sx, index=ix))


def portfolio_kwargs(**params):
    return {}
