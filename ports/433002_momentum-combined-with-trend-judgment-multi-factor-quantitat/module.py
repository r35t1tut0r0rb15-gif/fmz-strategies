"""HPotter's version of Dale Legan's Confluence indicator, broker days: three scores (error sum, momentum and trend, each
-3..3 from the sign, slope and signal of its line) are added; a bullish total of 1 or more with the long-minus-short
average spread positive goes long, a bearish one short, a grey (mixed) value goes flat, and zero keeps the state.
Port of FMZ strategy #433002 "Momentum Combined with Trend Judgment Multi factor Quantitative Trading Strategy" (Confluence).

FMZ source id: 433002

Source
    https://www.fmz.com/strategy/433002 (PineScript v2, FMZ last modified 2023-11-23 14:58:57).
    Verbatim copy: original_source.md. Read 2026-10-17 (FMZ-C).

Original signal (original_source.md lines 147-286), Harmonic 10 (STL 19, ITL 37, LTL 73; offsets 5 / 9 / 18), BuyBand 9, SellBand -9, reverse false
    xmomsig, xmom, xErrSum (sin + cos of the averages in degrees, phase-signed), xvalue70 = xvalue5 - xvalue13 and their signals
    ErrNum / momNum / TCNum = the 8-case iff ladders (-3..3);  value42 = their sum;  Confluence = value42, or value42 / 10 when its sign disagrees with xvalue70
    pos = Res2 >= -9 and Res2 != 0 ? -1 : Res1 <= 9 and Res1 != 0 ? 1 : Res3 != 0 ? 0 : pos[1];  1 -> long, -1 -> short, 0 -> close

Interpretation choices (Pine rules in SURVEY_README.md)
    * Every line is transcribed one for one, including the 3.14 approximation of pi in the sin / cos
      terms (degrees of a price, as written) and Pine's round() (ties up) for the derived lengths.
    * With BuyBand 9 / SellBand -9 the bands never bind (the total is between -9 and 9): any bullish
      value goes long, any bearish short. The ladders give 0 when a comparison is undefined.
    * strategy.entry reverses: REVERSAL INTENDED. reverse is false. Daily bars are broker days
      (17:00 America/New_York), stamped with their first minute. FREQ = "1D" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, score ladders of moving-average differences (the sin / cos terms are scale-bound, as written).
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (3 trials), before any backtest.
    6 near-duplicates: ND433002 (2 members, best partner #436148, Jaccard 0.783); ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: broker day (17:00 America/New_York, DST by the zone); no venue-open rule.
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_433002_confluence_state"
FAMILY = "multi_indicator_confluence"  # proposed 2026-10-17 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "harmonic": [10, 5, 20],
}
DEFAULT_PARAMS = {"harmonic": 10, "buy_band": 9.0, "sell_band": -9.0}


def broker_day(index):
    """Broker day of each timestamp: the session ending 17:00 America/New_York, labelled by its
    end date (as worker A's ports). The desktop binds this name to registry_schema.broker_day."""
    ny = index.tz_convert("America/New_York")
    return (ny + pd.Timedelta(hours=7)).normalize().tz_localize(None)


def precompute(raw_1m_df, symbol_key, **params):
    df = raw_1m_df[["open", "high", "low", "close"]].dropna(how="all")
    if df.index.tz is None:
        raise ValueError("raw_1m_df must have a tz-aware UTC index")
    lab = broker_day(df.index)
    bars = df.groupby(lab).agg({"open": "first", "high": "max", "low": "min", "close": "last"})
    first = pd.Series(df.index, index=df.index).groupby(lab).first()
    bars.index = pd.DatetimeIndex(first.loc[bars.index].values)   # each bar stamped with its first minute
    if bars.index.tz is None:
        bars.index = bars.index.tz_localize("UTC")
    return bars


def _pround(x):
    return int(np.floor(x + 0.5))


def _ladder(x, sig):
    x1 = x.shift(1)
    conds = [(x > 0) & (x < x1) & (x < sig), (x > 0) & (x < x1) & (x > sig), (x > 0) & (x > x1) & (x < sig),
             (x > 0) & (x > x1) & (x > sig), (x < 0) & (x > x1) & (x > sig), (x < 0) & (x < x1) & (x > sig),
             (x < 0) & (x > x1) & (x < sig), (x < 0) & (x < x1) & (x < sig)]
    return pd.Series(np.select(conds, [1, 2, 2, 3, -1, -2, -2, -3], 0), index=x.index).astype(float)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    o, h, lo, c = (bars_df[k] for k in ("open", "high", "low", "close"))
    hh = int(p["harmonic"])
    stl = _pround(hh * 2 - 1 - 0.5)
    itl = _pround(stl * 2 - 1 - 0.5)
    ltl = _pround(itl * 2 - 1 - 0.5)
    hoff, soff, ioff = _pround(hh / 2 - 0.5), _pround(stl / 2 - 0.5), _pround(itl / 2 - 0.5)

    def sma(x, n):
        return x.rolling(int(n)).mean()

    havg, savg, iavg, lavg = sma(c, hh), sma(c, stl), sma(c, itl), sma(c, ltl)
    momsig = (savg - havg.shift(hoff)) + (iavg - savg.shift(soff)) + (lavg - iavg.shift(ioff))
    lavg_ohlc = sma((o + h + lo + c) / 4, ltl - 1)
    h2, s2, i2, l2 = sma(c, hh - 1), sma(c, stl - 1), sma(c, itl - 1), sma(c, ltl - 1)
    drh = hh * (havg * 2 - havg.shift(1)) - h2 * (hh - 1)
    drs = stl * (savg * 2 - savg.shift(1)) - s2 * (stl - 1)
    dri = itl * (iavg * 2 - iavg.shift(1)) - i2 * (itl - 1)
    drl = ltl * (lavg * 2 - lavg.shift(1)) - l2 * (ltl - 1)
    v5 = (h2 * (hh - 1) + drh) / hh
    v6 = (s2 * (stl - 1) + drs) / stl
    v7 = (i2 * (itl - 1) + dri) / itl
    v13 = (lavg_ohlc * (ltl - 1) + drl) / ltl
    mom = (v6 - v5.shift(hoff)) + (v7 - v6.shift(soff)) + (v13 - v7.shift(ioff))
    k = 2 * 3.14 / 360

    def sc(x):
        return np.sin(x * k) + np.cos(x * k)

    xsum = sc(v5) + sc(v6) + sc(v7)
    xerr = sc(havg) + sc(savg) + sc(iavg)
    cond2 = ((xsum > xsum.shift(soff)) & (havg < havg.shift(soff))) | ((xsum < xsum.shift(soff))
                                                                       & (havg > havg.shift(soff)))
    phase = pd.Series(np.where(cond2, -1.0, 1.0), index=c.index)
    errsum = (xsum - xerr) * phase
    errsig = sma(errsum, soff)
    v70 = v5 - v13
    v71 = sma(v70, hh)
    v42 = _ladder(errsum, errsig) + _ladder(mom, momsig) + _ladder(v70, v71)
    conf = np.where((v42 > 0) & (v70 > 0), v42, np.where((v42 < 0) & (v70 < 0), v42,
                    np.where(((v42 > 0) & (v70 < 0)) | ((v42 < 0) & (v70 > 0)), v42 / 10, 0.0)))
    res1 = np.where(conf >= 1, conf, 0.0)
    res2 = np.where(conf <= -1, conf, 0.0)
    res3 = np.where(conf == 0, 0.0, np.where((conf > -1) & (conf < 1), 10 * conf, 0.0))
    m = len(c)
    tgt = np.zeros(m, dtype=np.int8)
    pos = 0
    for i in range(m):
        if res2[i] >= p["sell_band"] and res2[i] != 0:
            pos = -1
        elif res1[i] <= p["buy_band"] and res1[i] != 0:
            pos = 1
        elif res3[i] != 0:
            pos = 0
        tgt[i] = pos
    prev = np.concatenate(([0], tgt[:-1]))
    ix = bars_df.index
    return (pd.Series((tgt == 1) & (prev != 1), index=ix), pd.Series((prev == 1) & (tgt == 0), index=ix),
            pd.Series((tgt == -1) & (prev != -1), index=ix), pd.Series((prev == -1) & (tgt == 0), index=ix))


def portfolio_kwargs(**params):
    return {}
