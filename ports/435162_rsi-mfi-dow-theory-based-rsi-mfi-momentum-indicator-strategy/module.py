"""Broker days: an RSI 5 re-weighted by the 5-bar correlation of close and volume (the "Dow factor") crossing over 50 goes long, under 50 goes short; a bar where the "stagnant" odds exceed both the bull and bear odds closes; reversing.
Port of FMZ strategy #435162 "基于道氏理论的RSI-MFI动量指标策略Dow-Theory-based-RSI-MFI-Momentum-Indicator-Strategy" (Dow Factor RSI/MFI and Dependent Variable Odd Generator Strategy (Noldo)).

FMZ source id: 435162

Source
    https://www.fmz.com/strategy/435162 (PineScript v4, FMZ last modified 2023-12-12 17:54:58).
    Verbatim copy: original_source.md. Read 2026-10-23 (FMZ-C).

Original signal (original_source.md lines 136-341), method RSI; period 5; oversold / overbought 25 / 75 (plots and alerts only)
    dow_coeff = pearson(close, volume, 5) (EMA-centred);  bull = RSI 5 split into pure bull / bear / stagnant shares;  value = bull x (1 + coeff) / ((bull x (1 + coeff) + bear x (1 - coeff)) / 100)
    crossover(value, 50) -> entry Long;  crossunder(value, 50) -> entry Short;  odd_stagnant > odd_bull and > odd_bear -> close Long / close Short

Interpretation choices (Pine rules in SURVEY_README.md)
    * Method RSI (the default "RSI"; MFI off). The script's own RSI uses its f_rma, a recursive average
      started from 0 (nz), and the correlation centres each series on its own EMA 5 (started from the first
      value). The odds chain runs as written. A close acts only on a position the bar's entries leave
      unchanged (call order). The correlation of close with volume is unit-free. REVERSAL INTENDED. 100 %
      of equity and the commission are sizing and costs. Daily bars are broker days (17:00
      America/New_York), stamped with their first minute. FREQ = "1D" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, price-volume-correlation weighted RSI crossings.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: strategy(): 100 % of equity, commission 0.125 %, not ported.
    5 ranges declared: GRID below (2 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: used: the bars' volume column (broker tick volume of the cTrader M1 data, summed per bar) in the 5-bar Pearson correlation of close and volume (the Dow factor); exchange volume to be compared later (Austin, 2026-10-23).
Session open: broker day (17:00 America/New_York, DST by the zone); no venue-open rule.
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_435162_dow_factor_rsi5_volume_correlation_50_cross_reversal"
FAMILY = "rsi_threshold"  # proposed 2026-10-23 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "length": [5, 10],
}
DEFAULT_PARAMS = {"length": 5}


def broker_day(index):
    """Broker day of each timestamp: the session ending 17:00 America/New_York, labelled by its
    end date (as worker A's ports). The desktop binds this name to registry_schema.broker_day."""
    ny = index.tz_convert("America/New_York")
    return (ny + pd.Timedelta(hours=7)).normalize().tz_localize(None)


def precompute(raw_1m_df, symbol_key, **params):
    df = raw_1m_df[["open", "high", "low", "close", "volume"]].dropna(subset=["close"])
    if df.index.tz is None:
        raise ValueError("raw_1m_df must have a tz-aware UTC index")
    lab = broker_day(df.index)
    bars = df.groupby(lab).agg({"open": "first", "high": "max", "low": "min", "close": "last", "volume": "sum"})
    first = pd.Series(df.index, index=df.index).groupby(lab).first()
    bars.index = pd.DatetimeIndex(first.loc[bars.index].values)   # each bar stamped with its first minute
    if bars.index.tz is None:
        bars.index = bars.index.tz_localize("UTC")
    return bars


def _f_rma(x, n):
    """The source's f_rma: sum := (x + (n - 1) x nz(sum[1])) / n."""
    v = x.to_numpy(dtype=float)
    out = np.full(len(v), np.nan)
    prev = np.nan
    for i in range(len(v)):
        out[i] = (v[i] + (n - 1) * (0.0 if np.isnan(prev) else prev)) / n
        prev = out[i]
    return pd.Series(out, index=x.index)


def _pearson(a, b, n):
    ea = a.ewm(span=n, adjust=False).mean().to_numpy()
    eb = b.ewm(span=n, adjust=False).mean().to_numpy()
    av, bv = a.to_numpy(dtype=float), b.to_numpy(dtype=float)
    out = np.full(len(av), np.nan)
    if len(av) >= n:
        wa = np.lib.stride_tricks.sliding_window_view(av, n)
        wb = np.lib.stride_tricks.sliding_window_view(bv, n)
        da, db = wa - ea[n - 1:, None], wb - eb[n - 1:, None]
        with np.errstate(invalid="ignore", divide="ignore"):
            out[n - 1:] = (da * db).sum(axis=1) / np.sqrt((da ** 2).sum(axis=1) * (db ** 2).sum(axis=1))
    return out


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    c, v = bars_df["close"], bars_df["volume"]
    n = int(p["length"])
    r = _pearson(c, v, n)
    d = c.diff()
    with np.errstate(invalid="ignore", divide="ignore"):
        rs = (_f_rma(d.clip(lower=0), n) / _f_rma((-d).clip(lower=0), n)).to_numpy()
        meth = 100 - 100 / (1 + rs)
        bull_g, bear_g = meth, 100 - meth
        stag = bull_g * bear_g / 100
        p_bull, p_bear = bull_g - stag, bear_g - stag
        cp = (stag + p_bull + p_bear) / 100
        bull, bear = p_bull / cp, p_bear / cp
        tbg, tbr = bull * (1 + r), bear * (1 - r)
        value = tbg / ((tbg + tbr) / 100)
        ts = tbg * tbr / 100
        tb, tr_ = tbg - ts, tbr - ts
    val = pd.Series(value, index=c.index)
    pos_c = ((val > 50) & (val.shift(1) <= 50)).to_numpy()
    neg_c = ((val < 50) & (val.shift(1) >= 50)).to_numpy()
    stat = (ts > tb) & (ts > tr_)
    m = len(c)
    le, lx = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    se, sx = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    pos = 0
    for i in range(m):
        if pos_c[i] and pos != 1:
            le[i], pos = True, 1
        elif neg_c[i] and pos != -1:
            se[i], pos = True, -1
        elif stat[i] and pos == 1:
            lx[i], pos = True, 0
        elif stat[i] and pos == -1:
            sx[i], pos = True, 0
    ix = bars_df.index
    return (pd.Series(le, index=ix), pd.Series(lx, index=ix),
            pd.Series(se, index=ix), pd.Series(sx, index=ix))


def portfolio_kwargs(**params):
    return {}
