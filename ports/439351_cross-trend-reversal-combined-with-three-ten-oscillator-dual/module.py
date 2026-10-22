"""123 reversal and daily 3-10 oscillator combo, 5-minute bars: long when the 123 state (two-bar close pattern with the stochastic 14) and the 3-10 oscillator of the previous broker day's hl2 are both up,
short when both are down, flat when they disagree.
Port of FMZ strategy #439351 "Cross Trend Reversal Combined with Three Ten Oscillator Dual Strategies" (Combo Backtest 123 Reversal & D_Three Ten Osc).

FMZ source id: 439351

Source
    https://www.fmz.com/strategy/439351 (PineScript v4, FMZ last modified 2024-01-19 14:41:02).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 238-279), 123: length 14, K smoothing 1, D 3, level 50; 3-10: 3 / 10 / 16 on security("D", hl2); reverse off
    123 pos = 1 if close[2] < close[1] < close and vFast < vSlow and vFast > 50; -1 if mirrored; else previous
    3-10 pos = -1 if sma(ema3 - ema10, 16) > macd, 1 if below, else previous (on xPrice = security("D", hl2));  both 1 -> entry Long, both -1 -> entry Short, otherwise close_all

Interpretation choices (Pine rules in SURVEY_README.md)
    * A version-4 security() without lookahead is read as the last completed higher bar: xPrice is the
      previous broker day's hl2 on every 5-minute bar, built from the module's own bars; the EMAs and
      the SMA then run on the 5-minute series, as written. The 123 test is read as written. The states
      are levels; disagreement closes. REVERSAL INTENDED. No sizing code. FREQ = "5min" from the backtest
      header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; daily values from completed days.
    2 generic: PASS, close pattern, stochastic and an oscillator of daily hl2.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: broker day for the daily hl2 (17:00 America/New_York, DST by the zone).
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_439351_reversal123_daily_three_ten_combo"
FAMILY = "combo_123_reversal"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "5min"  # backtest header period: 5m
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "length": [14, 9],
    "length3": [16, 8],
}
DEFAULT_PARAMS = {"length": 14, "length3": 16, "k_smoothing": 1, "d_length": 3, "level": 50.0,
                  "length1": 3, "length2": 10, "reverse": False}


def _resample(raw_1m_df, freq):
    ohlc = raw_1m_df[["open", "high", "low", "close"]]
    bars = ohlc.resample(freq, label="left", closed="left").agg(
        {"open": "first", "high": "max", "low": "min", "close": "last"})
    bars = bars.dropna(how="all")  # an empty period is not a bar; never forward-filled
    if bars.index.tz is None:
        raise ValueError("raw_1m_df must have a tz-aware UTC index")
    return bars


def broker_day(index):
    """Broker day of each timestamp: the session ending 17:00 America/New_York, labelled by its
    end date (as worker A's ports). The desktop binds this name to registry_schema.broker_day."""
    ny = index.tz_convert("America/New_York")
    return (ny + pd.Timedelta(hours=7)).normalize().tz_localize(None)


def precompute(raw_1m_df, symbol_key, **params):
    return _resample(raw_1m_df, FREQ)


def _emit(tgt, index):
    prev = np.concatenate(([0], tgt[:-1]))
    le = (tgt == 1) & (prev != 1)
    lx = (prev == 1) & (tgt == 0)
    se = (tgt == -1) & (prev != -1)
    sx = (prev == -1) & (tgt == 0)
    return tuple(pd.Series(a, index=index) for a in (le, lx, se, sx))


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    n = int(p["length"])
    ll, hh = lo.rolling(n).min(), h.rolling(n).max()
    with np.errstate(divide="ignore", invalid="ignore"):
        st = 100.0 * (c - ll) / (hh - ll).where(hh > ll)
    vfast = st.rolling(int(p["k_smoothing"])).mean()
    vslow = vfast.rolling(int(p["d_length"])).mean()
    lvl = float(p["level"])
    c1, c2 = c.shift(1), c.shift(2)
    up_ = ((c2 < c1) & (c > c1) & (vfast < vslow) & (vfast > lvl)).to_numpy()
    dn_ = ((c2 > c1) & (c < c1) & (vfast > vslow) & (vfast < lvl)).to_numpy()
    day = broker_day(bars_df.index)
    d = bars_df.groupby(day).agg({"high": "max", "low": "min"})
    xp = ((d["high"] + d["low"]) / 2).shift(1).reindex(day)          # last completed day
    xp = pd.Series(xp.to_numpy(), index=c.index)
    macd = xp.ewm(span=int(p["length1"]), adjust=False).mean() - xp.ewm(span=int(p["length2"]), adjust=False).mean()
    sig = macd.rolling(int(p["length3"])).mean()
    s_dn, s_up = (sig > macd).to_numpy(), (sig < macd).to_numpy()
    m = len(c)
    tgt = np.zeros(m, dtype=np.int8)
    p123 = p310 = 0
    for i in range(m):
        if up_[i]:
            p123 = 1
        elif dn_[i]:
            p123 = -1
        if s_dn[i]:
            p310 = -1
        elif s_up[i]:
            p310 = 1
        tgt[i] = 1 if (p123 == 1 and p310 == 1) else (-1 if (p123 == -1 and p310 == -1) else 0)
    if p["reverse"]:
        tgt = -tgt
    return _emit(tgt, bars_df.index)


def portfolio_kwargs(**params):
    return {}
