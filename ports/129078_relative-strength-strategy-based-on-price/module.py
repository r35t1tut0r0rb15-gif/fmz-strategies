"""Volume-weighted close-location and body-direction ratios over 100 bars with the MA 100 side and 100-bar range breaks, hourly bars: both ratios bullish above the MA at a new 100-bar high goes long, the mirror goes short; a close 2 average ranges against the signal close, or a lost-MA after a 2-range run, closes; reversing.
Port of FMZ strategy #129078 "Relative Strength Strategy Based on Price" (Relative Strength Strategy Based on Price).

FMZ source id: 129078

Source
    https://www.fmz.com/strategy/129078 (MyLanguage, FMZ last modified 2018-12-18 10:25:23).
    Verbatim copy: original_source.md. Read 2026-10-23 (FMZ-C).

Original signal (original_source.md lines 58-88), MyLanguage (no AUTOFILTER); N 100; M 2; STOPLOSS = M x MA(H - L, N)
    B_K1 := SUM((C - L) V, N) / SUM((H - L) V, N) > 0.5;  B_K2 := SUM(CO V, N) / SUM(|C - O| V, N) > 0.5 (CO = C - O on up bars);  mirrors S_K1 / S_K2
    B_K1 and B_K2 and C > MA(C, N) and H >= HHV(H, N) -> BPK;  mirror and L <= LLV(L, N) -> SPK
    C < BKPRICE - STOPLOSS -> SP;  C > SKPRICE + STOPLOSS -> BP;  C < MA and BKHIGH > BKPRICE + STOPLOSS -> SP;  C > MA and SKLOW < SKPRICE - STOPLOSS -> BP

Interpretation choices (rules in SURVEY_README.md)
    * MyLanguage close-price model without AUTOFILTER (SURVEY_README MyLanguage rules): the statements run
      in source order on the completed bar, each on the position the earlier ones left; a BPK while long
      is an add (sizing, not ported) but still moves BKPRICE to that close; BPK / SPK reverse. BKPRICE /
      SKPRICE are signal-bar closes; BKHIGH / SKLOW the highest high / lowest low of the bars after it. The
      stops are close tests (exit signals). A zero denominator leaves its ratio false. REVERSAL INTENDED.
      No sizing code. FREQ = "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; close-based stops against the signal close.
    2 generic: PASS, volume-weighted bar-location ratios with MA side and range breaks.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: used: the bars' volume column (broker tick volume of the cTrader M1 data, summed per bar) as the weight in the four 100-bar ratios; exchange volume to be compared later (Austin, 2026-10-23).
Session open: not used.
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_129078_volume_weighted_bar_location_ma100_break_range_stop_reversal"
FAMILY = "momentum_breakout"  # proposed 2026-10-23 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "n": [100, 50],
    "m": [2.0, 3.0],
}
DEFAULT_PARAMS = {"n": 100, "m": 2.0}


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
    n = int(p["n"])

    def ratio(num, den):
        a, b = (num * v).rolling(n).sum(), (den * v).rolling(n).sum()
        return (a / b.where(b != 0)) > 0.5

    ma = c.rolling(n).mean()
    co = (c - o).where(c > o, 0.0)
    oc = (o - c).where(c < o, 0.0)
    b_go = (ratio(c - lo, h - lo) & ratio(co, (c - o).abs()) & (c > ma) & (h >= h.rolling(n).max())).to_numpy()
    s_go = (ratio(h - c, h - lo) & ratio(oc, (c - o).abs()) & (c < ma) & (lo <= lo.rolling(n).min())).to_numpy()
    b_ma, s_ma = (c > ma).to_numpy(), (c < ma).to_numpy()
    sl = (float(p["m"]) * (h - lo).rolling(n).mean()).to_numpy(dtype=float)
    hv, lv, cv = h.to_numpy(dtype=float), lo.to_numpy(dtype=float), c.to_numpy(dtype=float)
    m = len(cv)
    le, lx, se, sx = (np.zeros(m, dtype=bool) for _ in range(4))
    pos, px, ext = 0, np.nan, np.nan               # ext: BKHIGH / SKLOW since the signal bar
    for i in range(m):
        old = pos
        if pos == 1:
            ext = hv[i] if np.isnan(ext) else max(ext, hv[i])
        elif pos == -1:
            ext = lv[i] if np.isnan(ext) else min(ext, lv[i])
        if b_go[i]:                                # BPK (an add when long: BKPRICE moves)
            pos, px, ext = 1, cv[i], np.nan
        if s_go[i]:                                # SPK
            pos, px, ext = -1, cv[i], np.nan
        if pos == 1 and cv[i] < px - sl[i]:
            pos = 0
        if pos == -1 and cv[i] > px + sl[i]:
            pos = 0
        if pos == 1 and s_ma[i] and ext > px + sl[i]:
            pos = 0
        if pos == -1 and b_ma[i] and ext < px - sl[i]:
            pos = 0
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
