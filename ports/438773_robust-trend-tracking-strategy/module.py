"""123 reversal and Smart Money Index combination, 10-minute bars: the 123 reversal state and the SMI state (its 18-bar average above the running index: long; under: short) agreeing long go long, agreeing short
go short, disagreeing close all; reversing.
Port of FMZ strategy #438773 "Robust Trend Tracking Strategy" (Combo).

FMZ source id: 438773

Source
    https://www.fmz.com/strategy/438773 (PineScript v4, FMZ last modified 2024-01-15 11:52:53).
    Verbatim copy: original_source.md. Read 2026-10-21 (FMZ-C).

Original signal (original_source.md lines 170-212), 123: length 14, K smoothing 1, D 3, level 50; SMI length 18, resolution D; reverse off
    SMI: xclose / xopen = security(D, close[1] / open[1]);  nRes := nz(nRes[1], 1) - (open - close) + (xopen - xclose);  pos = 1 if sma(nRes, 18) > nRes, -1 if <, else pos[1]
    Reversal123 as in the combo family;  agree -> entry, else close_all

Interpretation choices (Pine rules in SURVEY_README.md)
    * A version-4 security() without lookahead is read as the last completed higher bar; its expression
      close[1] / open[1] is then the day before that, so both are the broker day two days back, built from
      the module's own bars. The running index adds that day's body on every 10-minute bar, as written;
      it restarts from 1 while the daily values are na. The 123 test is read as written. The states are
      levels; disagreement closes. REVERSAL INTENDED. No sizing code. FREQ = "10min" from the backtest
      header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; daily values from completed days.
    2 generic: PASS, close patterns, stochastic and a running bar-body index.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: broker day (17:00 America/New_York, DST by the zone) for the daily values.
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_438773_reversal123_smart_money_index_combo"
FAMILY = "combo_123_reversal"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "10min"  # backtest header period: 10m
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "length": [14, 9],
    "length_smi": [18, 36],
}
DEFAULT_PARAMS = {"length": 14, "length_smi": 18, "k_smoothing": 1, "d_length": 3, "level": 50.0,
                  "reverse": False}


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
    o, h, lo, c = (bars_df[k] for k in ("open", "high", "low", "close"))
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
    d = bars_df.groupby(day).agg({"open": "first", "close": "last"})
    xo = d["open"].shift(2).reindex(day).to_numpy()        # completed day, then [1]
    xc = d["close"].shift(2).reindex(day).to_numpy()
    ov, cv = o.to_numpy(dtype=float), c.to_numpy(dtype=float)
    m = len(cv)
    res = np.full(m, np.nan)
    for i in range(m):
        prev = res[i - 1] if i > 0 and not np.isnan(res[i - 1]) else 1.0   # nz(nRes[1], 1)
        res[i] = prev - (ov[i] - cv[i]) + (xo[i] - xc[i])
    rs = pd.Series(res, index=c.index)
    sm = rs.rolling(int(p["length_smi"])).mean().to_numpy()
    tgt = np.zeros(m, dtype=np.int8)
    p123 = psm = 0
    for i in range(m):
        if up_[i]:
            p123 = 1
        elif dn_[i]:
            p123 = -1
        if sm[i] > res[i]:
            psm = 1
        elif sm[i] < res[i]:
            psm = -1
        tgt[i] = 1 if (p123 == 1 and psm == 1) else (-1 if (p123 == -1 and psm == -1) else 0)
    if p["reverse"]:
        tgt = -tgt
    return _emit(tgt, bars_df.index)


def portfolio_kwargs(**params):
    return {}
