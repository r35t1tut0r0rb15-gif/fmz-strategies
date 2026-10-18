"""Dynamic moving-average and momentum slopes, 1-hour bars: when the volatility is normal, both smoothed slopes (of a TEMA
and of an RSI of the rate of change, read at the last minute of the bar) above +0.02 go long and both below -0.03 go
short (reversing); when the 10-bar average of the bar range is under 2.5 %, the slope of a 28-bar average decides.
Port of FMZ strategy #435265 "Dynamic Moving Average Dual Strategy" (DRSI DMA Scalping Strategy).

FMZ source id: 435265

Source
    https://www.fmz.com/strategy/435265 (PineScript v4, FMZ last modified 2023-12-13 16:37:05).
    Verbatim copy: original_source.md. Read 2026-10-18 (FMZ-C).

Original signal (original_source.md lines 183-258), TEMA 5 (type 7) slope 3 / smooth 5 x 130; RSI(ROC 3, 3) slope 8 / smooth 7; thresholds +0.02 / -0.03; low-volatility SMA 28, SMA 10 of the range, minimum 2.5 %
    percent_volatility = (1 - low / high) 100;  bad_vol = sma(percent_volatility, 10) < 2.5;  low_vol_up = low_vol_MA[3] - low_vol_MA[1] < -0.05;  low_vol_down = low_vol_MA[3] - low_vol_MA[1] > 0.05  (low_vol_MA = sma(close, 28))
    MAout = security(tickerid, "1", sma(avg / avg[3] - 1, 5)) 130;  Momout = security(tickerid, "1", sma(mom / mom[8] - 1, 7))
    longCondition = bad_vol ? low_vol_up : MAout > 0.02 and Momout > 0.02 -> entry long;  shortCondition = bad_vol ? low_vol_down : MAout < -0.03 and Momout < -0.03 -> entry short

Interpretation choices (Pine rules in SURVEY_README.md)
    * The "higher timeframe" input is "1" (one minute), a LOWER resolution than the 1-hour chart.
      security() then evaluates the whole slope expression on the 1-minute series (the look-backs 3,
      5, 8 and 7 are minutes) and gives the chart bar the value of its last minute. The port does
      the same: precompute builds the two slope columns on the loader's minutes and keeps each bar's
      last-minute value (known at the bar's end; no later minute is used). An infinite ratio (a zero
      denominator) counts as missing, so a comparison with it is false.
    * Criterion 2: the low-volatility threshold 0.05 is a price unit (about nothing on BTC); the port
      reads it as a fraction of the close, mt_frac (0.0 = the sign of the slope, 0.0005 = a
      band). The low-volatility average slope uses hourly bars as written. pyramiding = 2 lets the
      author add a second unit on a later signal; the port holds one unit (vbt ignores a same-side
      signal): sizing. strategy.entry reverses: REVERSAL INTENDED.
    * The 130 multiplier is the author's. FREQ = "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; the last-minute value is known at the bar's end.
    2 generic: ADAPT, price-unit threshold -> fraction of the close.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: the percent-of-equity size and pyramiding 2 stored.
    5 ranges declared: GRID below (8 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_435265_dynamic_ma_momentum_slopes"
FAMILY = "momentum_oscillator"  # proposed 2026-10-18 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "malen": [5, 10],
    "vol_min": [2.5, 1.0],
    "mt_frac": [0.0, 0.0005],
}
DEFAULT_PARAMS = {"malen": 5, "maderiv": 3, "masmooth": 5, "momlen": 3, "momderiv": 8, "momsmooth": 7, "mult": 130.0,
                  "buffup": 0.02, "bufflow": -0.03, "big_ma": 28, "ma_len": 10, "vol_min": 2.5, "mt_frac": 0.0}


def _rsi(x, n):
    ch = x.diff()
    up = ch.clip(lower=0).ewm(alpha=1 / n, adjust=False).mean()
    dn = (-ch.clip(upper=0)).ewm(alpha=1 / n, adjust=False).mean()
    return (100 - 100 / (1 + up / dn)).where(dn != 0, 100.0).where(up.notna())


def _slopes(close, p):
    """The two slope series on the 1-minute closes (security() at resolution "1")."""
    n = int(p["malen"])
    e1 = close.ewm(span=n, adjust=False).mean()
    e2 = e1.ewm(span=n, adjust=False).mean()
    e3 = e2.ewm(span=n, adjust=False).mean()
    avg = 3 * (e1 - e2) + e3
    d = int(p["maderiv"])
    with np.errstate(invalid="ignore", divide="ignore"):
        ma = (avg / avg.shift(d) - 1).replace([np.inf, -np.inf], np.nan).rolling(int(p["masmooth"])).mean() * float(p["mult"])
        L = int(p["momlen"])
        roc = 100 * (close - close.shift(L)) / close.shift(L)
        mom = _rsi(roc, L)
        dm = int(p["momderiv"])
        mo = (mom / mom.shift(dm) - 1).replace([np.inf, -np.inf], np.nan).rolling(int(p["momsmooth"])).mean()
    return ma, mo


def precompute(raw_1m_df, symbol_key, **params):
    p = {**DEFAULT_PARAMS, **params}
    ohlc = raw_1m_df[["open", "high", "low", "close"]]
    bars = ohlc.resample(FREQ, label="left", closed="left").agg(
        {"open": "first", "high": "max", "low": "min", "close": "last"})
    bars = bars.dropna(how="all")  # an empty period is not a bar; never forward-filled
    if bars.index.tz is None:
        raise ValueError("raw_1m_df must have a tz-aware UTC index")
    ma, mo = _slopes(ohlc["close"].dropna(), p)
    last = lambda s: s.resample(FREQ, label="left", closed="left").last().reindex(bars.index)  # noqa: E731
    bars["ma_out"] = last(ma)
    bars["mom_out"] = last(mo)
    return bars


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    big = c.rolling(int(p["big_ma"])).mean()
    chg = big.shift(3) - big.shift(1)                       # low_vol_MA[3] - low_vol_MA[1]
    thr = float(p["mt_frac"]) * c
    low_up = chg < -thr
    low_dn = chg > thr
    vol = ((1 - lo / h) * 100).rolling(int(p["ma_len"])).mean()
    bad = (vol < float(p["vol_min"])).to_numpy()
    ma, mo = bars_df["ma_out"], bars_df["mom_out"]
    lg = np.where(bad, low_up.to_numpy(), ((ma > float(p["buffup"])) & (mo > float(p["buffup"]))).to_numpy())
    sh = np.where(bad, low_dn.to_numpy(), ((ma < float(p["bufflow"])) & (mo < float(p["bufflow"]))).to_numpy())
    ix = bars_df.index
    false = pd.Series(False, index=ix)
    return pd.Series(lg.astype(bool), index=ix), false, pd.Series(sh.astype(bool), index=ix), false.copy()


def portfolio_kwargs(**params):
    return {}
