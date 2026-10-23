"""HPotter combo, broker days: the 123-reversal state (stochastic 14 / 1 / 3 at 50) and a volume state (+1 when volume is under its SMA 40, -1 when above) both long goes long, both short goes short, any disagreement closes; reversing.
Port of FMZ strategy #442504 "Bi directional Reversal Quantitative Trading Strategy" (Combo Backtest 123 Reversal & Volume SMA (HPotter)).

FMZ source id: 442504

Source
    https://www.fmz.com/strategy/442504 (PineScript v4, FMZ last modified 2024-02-22 13:46:51).
    Verbatim copy: original_source.md. Read 2026-10-23 (FMZ-C).

Original signal (original_source.md lines 134-169), 123 reversal: length 14, K smoothing 1, D length 3, level 50; volume SMA 40; reverse off
    posVSAVol = volume > sma(volume, 40) ? -1 : volume < sma ? 1 : pos[1]
    pos = both 1 ? 1 : both -1 ? -1 : 0;  1 -> entry Long, -1 -> entry Short, 0 -> close_all

Interpretation choices (Pine rules in SURVEY_README.md)
    * The volume state is long on below-average volume and short on above-average volume, as written.
      reverse is off. REVERSAL INTENDED. No sizing code. Daily bars are broker days (17:00
      America/New_York), stamped with their first minute. FREQ = "1D" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, combined price-pattern and volume states.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: used: the bars' volume column (broker tick volume of the cTrader M1 data, summed per bar) against its SMA 40; exchange volume to be compared later (Austin, 2026-10-23).
Session open: broker day (17:00 America/New_York, DST by the zone); no venue-open rule.
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_442504_reversal123_volume_sma_combo_reversal"
FAMILY = "hpotter_combo"  # proposed 2026-10-23 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "length": [14, 9],
    "vol_len": [40, 20],
}
DEFAULT_PARAMS = {"length": 14, "k_smooth": 1, "d_len": 3, "level": 50.0, "vol_len": 40}


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
    sv = v.rolling(int(p["vol_len"])).mean()
    raw = np.where(v > sv, -1, np.where(v < sv, 1, 0))
    m = len(raw)
    vs = np.zeros(m, dtype=np.int8)
    q = 0
    for i in range(m):
        if raw[i] != 0:
            q = raw[i]
        vs[i] = q
    s = np.where((r123 == 1) & (vs == 1), 1, np.where((r123 == -1) & (vs == -1), -1, 0))
    le, lx = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    se, sx = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    pos = 0
    for i in range(m):
        if s[i] == 1 and pos != 1:
            le[i], pos = True, 1
        elif s[i] == -1 and pos != -1:
            se[i], pos = True, -1
        elif s[i] == 0 and pos == 1:
            lx[i], pos = True, 0
        elif s[i] == 0 and pos == -1:
            sx[i], pos = True, 0
    ix = bars_df.index
    return (pd.Series(le, index=ix), pd.Series(lx, index=ix),
            pd.Series(se, index=ix), pd.Series(sx, index=ix))


def portfolio_kwargs(**params):
    return {}
