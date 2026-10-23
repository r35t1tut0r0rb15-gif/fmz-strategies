"""A 26-bar "polynomial regression" of the high and low on the bar index and its square root (as written, with the source's sqrt terms), 4-hour bars: a strict local top of the high curve 3 bars back goes long and a strict local bottom of the low curve goes short, both only while the angle of a cumulative VWAP exceeds 26.8 degrees; a close beyond 5.6 % or 1.4 % of the signal close closes; reversing.
Port of FMZ strategy #426323 "Quantitative Trend Trading Strategy Using Polynomial Regression" (Quantitative Trend Trading Strategy Using Polynomial Regression (underground09)).

FMZ source id: 426323

Source
    https://www.fmz.com/strategy/426323 (PineScript v4, FMZ last modified 2023-09-11 09:04:37).
    Verbatim copy: original_source.md. Read 2026-10-23 (FMZ-C).

Original signal (original_source.md lines 88-240), p 4, length 26; angle 26.8; SL 1.4 %, TP 5.6 % of the signal close (close tests); strategy() commented out
    qr = b1 + b2 x bar_index + b3 x sqrt(bar_index) (sums over 26 bars, as written);  buy = qr[3] above qr[1..2] and qr[4..5];  sell = qrl[3] below qrl[1..2] and qrl[4..5]
    pendiente = atan(vwap2 - vwap2[1]) x 180 / pi, vwap2 = cum(volume x hlc3) / cum(volume);  buy and pendiente > 26.8 -> entry long, sl / tp from the close;  sell and pendiente > 26.8 -> entry short
    long and close >= tp or close <= sl -> close long;  short mirror

Interpretation choices (Pine rules in SURVEY_README.md)
    * The regression sums are kept exactly as written (S11 = sum(sqrt x) - sqrt(sum(x)) / n, S22 with
      sqrt(sqrt x), denominators with sqrt(S12)); bar_index counts from the first loaded bar, so the curves
      depend on where the data starts. A top of the HIGH curve goes long and a bottom of the LOW curve goes
      short, as written. The cumulative VWAP also runs from the first loaded bar, and its angle is
      atan(price change per bar) in degrees: a raw price distance (0.5 price units per bar for 26.8
      degrees), and both sides need it rising, as written. Every signal resets sl / tp to its own close,
      also a repeat signal that does not trade. The close tests act only on a position the bar's entries
      leave unchanged. pyramiding is commented out (the default 1). REVERSAL INTENDED. The equity / close
      quantity is sizing. FREQ = "4h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; close-based target / stop.
    2 generic: PASS, regression-curve turning points with a VWAP-angle filter.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: qty = round(equity / close) and the commented strategy() stored, not ported.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: used: the bars' volume column (broker tick volume of the cTrader M1 data, summed per bar) in the cumulative VWAP cum(volume x hlc3) / cum(volume) whose angle gates both entries; exchange volume to be compared later (Austin, 2026-10-23).
Session open: not used (the author's 2019 .. 9999 window is not used by the orders).
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_426323_index_sqrt_regression_turning_point_vwap_angle_close_bracket_reversal"
FAMILY = "regression_channel"  # proposed 2026-10-23 (FMZ-C), user to confirm
FREQ = "4h"  # backtest header period: 4h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "length": [26, 30],
    "angulo": [26.8, 10.0],
}
DEFAULT_PARAMS = {"length": 26, "angulo": 26.8, "p": 4, "stop_loss": 1.4, "take_profit": 5.6}


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


def _curve(y, x1, x2, n):
    """The source's regression of y on bar_index and sqrt(bar_index), formulas as written."""
    s = lambda a: a.rolling(n).sum()
    s11 = s(x2) - np.sqrt(s(x1)) / n
    s12 = s(x1 * x2) - (s(x1) * s(x2)) / n
    s22 = s(np.sqrt(x2)) - np.sqrt(s(x2)) / n
    sy1 = s(y * x1) - (s(y) * s(x1)) / n
    sy2 = s(y * x2) - (s(y) * s(x2)) / n
    den = s22 * s11 - np.sqrt(s12)
    b2 = (sy1 * s22 - sy2 * s12) / den
    b3 = (sy2 * s11 - sy1 * s12) / den
    b1 = y.rolling(n).mean() - b2 * x1.rolling(n).mean() - b3 * x2.rolling(n).mean()
    return b1 + b2 * x1 + b3 * x2


def _signals(bars_df, prm):
    h, lo, c, v = (bars_df[k] for k in ("high", "low", "close", "volume"))
    n, p = int(prm["length"]), int(prm["p"])
    x1 = pd.Series(np.arange(len(c), dtype=float), index=c.index)
    x2 = np.sqrt(x1)
    with np.errstate(invalid="ignore", divide="ignore"):
        qr, qrl = _curve(h, x1, x2, n), _curve(lo, x1, x2, n)
    period = int(np.floor(p / 2 + 0.5)) + 1
    hh, ll = qr.shift(period), qrl.shift(period)
    count_h = sum((qr.shift(i) < hh).astype(int) for i in list(range(1, period)) + list(range(period + 1, p + 2)))
    count_l = sum((qrl.shift(i) > ll).astype(int) for i in list(range(1, period)) + list(range(period + 1, p + 2)))
    buy, sell = count_h == p, count_l == p
    vwap2 = (v * (h + lo + c) / 3).cumsum() / v.cumsum()
    ang = np.degrees(np.arctan(vwap2 - vwap2.shift(1)))
    ok = ang > float(prm["angulo"])
    return (buy & ok).to_numpy(), (sell & ok).to_numpy()


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    buy, sell = _signals(bars_df, p)
    cv = bars_df["close"].to_numpy(dtype=float)
    k_sl, k_tp = float(p["stop_loss"]) / 100, float(p["take_profit"]) / 100
    m = len(cv)
    le, lx, se, sx = (np.zeros(m, dtype=bool) for _ in range(4))
    pos, sl, tp = 0, 0.0, 0.0
    for i in range(m):
        old = pos
        if buy[i]:
            pos, sl, tp = 1, cv[i] * (1 - k_sl), cv[i] * (1 + k_tp)
        if sell[i]:
            pos, sl, tp = -1, cv[i] * (1 + k_sl), cv[i] * (1 - k_tp)
        if pos == old == 1 and (cv[i] >= tp or cv[i] <= sl):
            pos = 0
        elif pos == old == -1 and (cv[i] <= tp or cv[i] >= sl):
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
