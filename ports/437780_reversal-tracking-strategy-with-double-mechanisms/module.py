"""HPotter combo, broker days: the 123-reversal state (stochastic 14 / 1 / 3 at 50) and the Positive Volume Index state (a running sum of the 1-bar rate of change on bars whose volume rose, against its EMA 255) both long goes long, both short goes short, any disagreement closes; reversing.
Port of FMZ strategy #437780 "Reversal Tracking Strategy with Double Mechanisms" (Combo Backtest 123 Reversal & Positive Volume Index (HPotter)).

FMZ source id: 437780

Source
    https://www.fmz.com/strategy/437780 (PineScript v4, FMZ last modified 2024-01-05 15:09:19).
    Verbatim copy: original_source.md. Read 2026-10-23 (FMZ-C).

Original signal (original_source.md lines 236-277), 123 reversal: length 14, K smoothing 1, D length 3, level 50; PVI EMA 255; reverse off
    nRes := volume > volume[1] ? nz(nRes[1]) + roc(close, 1) : nz(nRes[1]);  posPVI = nRes > ema(nRes, 255) ? 1 : nRes < ema ? -1 : pos[1]
    pos = both 1 ? 1 : both -1 ? -1 : 0;  1 -> entry Long, -1 -> entry Short, 0 -> close_all

Interpretation choices (Pine rules in SURVEY_README.md)
    * The PVI only compares each bar's volume with the previous one. The running sum starts at 0 (nz).
      reverse is off. REVERSAL INTENDED. No sizing code. Daily bars are broker days (17:00
      America/New_York), stamped with their first minute. FREQ = "1D" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, combined price-pattern and positive-volume-index states.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: used: the bars' volume column (broker tick volume of the cTrader M1 data, summed per bar) in the Positive Volume Index test volume > volume[1]; exchange volume to be compared later (Austin, 2026-10-23).
Session open: broker day (17:00 America/New_York, DST by the zone); no venue-open rule.
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_437780_reversal123_positive_volume_index_combo_reversal"
FAMILY = "hpotter_combo"  # proposed 2026-10-23 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "ema_len": [255, 100],
    "length": [14, 9],
}
DEFAULT_PARAMS = {"length": 14, "k_smooth": 1, "d_len": 3, "level": 50.0, "ema_len": 255}


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


def _reversal123(h, lo, c, length, k_smooth, d_len, level):
    """Pine's Reversal123 state: 1 / -1 on the pattern, else the last state (0 before any)."""
    with np.errstate(invalid="ignore", divide="ignore"):
        raw = 100 * (c - lo.rolling(length).min()) / (h.rolling(length).max() - lo.rolling(length).min())
    vf = raw.rolling(k_smooth).mean()
    vs = vf.rolling(d_len).mean()
    c1, c2 = c.shift(1), c.shift(2)
    up = ((c2 < c1) & (c > c1) & (vf < vs) & (vf > level)).to_numpy()
    dn = ((c2 > c1) & (c < c1) & (vf > vs) & (vf < level)).to_numpy()
    out = np.zeros(len(up), dtype=np.int8)
    q = 0
    for i in range(len(up)):
        if up[i]:
            q = 1
        elif dn[i]:
            q = -1
        out[i] = q
    return out


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    h, lo, c, v = (bars_df[k] for k in ("high", "low", "close", "volume"))
    r123 = _reversal123(h, lo, c, int(p["length"]), int(p["k_smooth"]), int(p["d_len"]), float(p["level"]))
    roc = (100 * (c - c.shift(1)) / c.shift(1)).to_numpy()
    vup = (v > v.shift(1)).to_numpy()
    m = len(roc)
    res = np.zeros(m)
    prev = 0.0
    for i in range(m):
        cur = prev + roc[i] if vup[i] else prev
        res[i] = cur
        prev = 0.0 if np.isnan(cur) else cur
    rs = pd.Series(res, index=c.index)
    e = rs.ewm(span=int(p["ema_len"]), adjust=False).mean()
    raw = np.where(rs > e, 1, np.where(rs < e, -1, 0))
    pv = np.zeros(m, dtype=np.int8)
    q = 0
    for i in range(m):
        if raw[i] != 0:
            q = raw[i]
        pv[i] = q
    sig = np.where((r123 == 1) & (pv == 1), 1, np.where((r123 == -1) & (pv == -1), -1, 0))
    le, lx = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    se, sx = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    pos = 0
    for i in range(m):
        if sig[i] == 1 and pos != 1:
            le[i], pos = True, 1
        elif sig[i] == -1 and pos != -1:
            se[i], pos = True, -1
        elif sig[i] == 0 and pos == 1:
            lx[i], pos = True, 0
        elif sig[i] == 0 and pos == -1:
            sx[i], pos = True, 0
    ix = bars_df.index
    return (pd.Series(le, index=ix), pd.Series(lx, index=ix),
            pd.Series(se, index=ix), pd.Series(sx, index=ix))


def portfolio_kwargs(**params):
    return {}
