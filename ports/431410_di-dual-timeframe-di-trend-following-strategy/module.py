"""DI+ over DI- trend following (DojiEmoji), broker days, long only: +DI above -DI goes long; a low at or under the previous
bar's ratcheting stop (the highest low - 2 ATR 14 since entry) closes the long.
Port of FMZ strategy #431410 "多时间框架趋势跟踪DI策略Dual-Timeframe-DI-Trend-Following-Strategy" (DI+/- multi TF Strat [KL]).

FMZ source id: 431410

Source
    https://www.fmz.com/strategy/431410 (PineScript v5, FMZ last modified 2023-11-07 16:31:07).
    Verbatim copy: original_source.md. Read 2026-10-17 (FMZ-C).

Original signal (original_source.md lines 186-274), DI 14 (Wilder sums), timeframes "" and 1D (both the daily chart), ATR 14 x 2
    long = +DI > -DI on tf1 and on tf2 -> entry long, pos_opened = true
    stop := pos_opened ? max(stop, low - 2 ATR) : low - 2 ATR
    pos_opened and low <= stop -> close;  pos_opened -> exit(stop = stop) every bar

Interpretation choices (Pine rules in SURVEY_README.md)
    * tf2 = 1D is the header's own daily chart, so both DI pairs are the chart's (the source's own
      Wilder-sum DI). The close-checked exit (low at or under the stop as raised on this bar, i.e. the
      previous bar's stop level) is ported; the resting stop order at the ratcheting low - 2 ATR (a
      level on the bars' lows, not the best price) is not expressible by the house trail: rule 2,
      mark trailing_stop_pending, not emitted.
    * The close is written before the entry: a bar that closes and still meets the entry stays long
      (close then re-entry). The 2020 start is dropped. Long only; Opposite entries cannot occur.
      Daily bars are broker days (17:00 America/New_York), stamped with their first minute.
      FREQ = "1D" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; close-checked exit.
    2 generic: PASS, DI comparison and ATR multiples.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: 5 % of equity stored in original_sizing.txt.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: broker day (17:00 America/New_York, DST by the zone); no venue-open rule.
Long only. Opposite entries cannot occur.

Marks: trailing_stop_pending
"""
import numpy as np
import pandas as pd

NAME = "fmz_431410_di_trend_ratchet_long"
FAMILY = "directional_movement"  # proposed 2026-10-17 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "adx_len": [14, 28],
    "tsl_mult": [2.0, 3.0],
}
DEFAULT_PARAMS = {"adx_len": 14, "atr_len": 14, "tsl_mult": 2.0}


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


def _rma(x, n):
    """Wilder smoothing as TA-Lib: SMA seed over the first n valid values, then recursive."""
    v = np.asarray(x, dtype=float)
    out = np.full(v.shape, np.nan)
    valid = np.flatnonzero(~np.isnan(v))
    if len(valid) >= n:
        s = valid[0]
        out[s + n - 1] = v[s:s + n].mean()
        for i in range(s + n, len(v)):
            out[i] = (out[i - 1] * (n - 1) + v[i]) / n
    return out


def _emit(tgt, index):
    prev = np.concatenate(([0], tgt[:-1]))
    le = (tgt == 1) & (prev != 1)
    lx = (prev == 1) & (tgt == 0)
    se = (tgt == -1) & (prev != -1)
    sx = (prev == -1) & (tgt == 0)
    return tuple(pd.Series(a, index=index) for a in (le, lx, se, sx))


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    hv, lv, cv = (bars_df[k].to_numpy(dtype=float) for k in ("high", "low", "close"))
    m = len(cv)
    n = int(p["adx_len"])
    s_tr = s_p = s_m = 0.0
    di_up = np.zeros(m, dtype=bool)
    tr = np.zeros(m)
    for i in range(m):
        c1 = cv[i - 1] if i else 0.0
        h1 = hv[i - 1] if i else 0.0
        l1 = lv[i - 1] if i else 0.0
        t = max(hv[i] - lv[i], abs(hv[i] - c1), abs(lv[i] - c1))
        tr[i] = max(hv[i] - lv[i], abs(hv[i] - cv[i - 1]), abs(lv[i] - cv[i - 1])) if i else hv[i] - lv[i]
        dp = max(hv[i] - h1, 0) if hv[i] - h1 > l1 - lv[i] else 0.0
        dm = max(l1 - lv[i], 0) if l1 - lv[i] > hv[i] - h1 else 0.0
        s_tr = s_tr - s_tr / n + t
        s_p = s_p - s_p / n + dp
        s_m = s_m - s_m / n + dm
        di_up[i] = s_p / s_tr * 100 > s_m / s_tr * 100 if s_tr else False
    buf = _rma(tr, int(p["atr_len"])) * float(p["tsl_mult"])
    tgt = np.zeros(m, dtype=np.int8)
    opened, stop = False, 0.0
    for i in range(m):
        stop = max(stop, lv[i] - buf[i]) if opened else lv[i] - buf[i]
        if opened and lv[i] <= stop:
            opened = False
        if di_up[i]:
            opened = True
        if not opened:
            stop = 0.0
        tgt[i] = 1 if opened else 0
    return _emit(tgt, bars_df.index)


def portfolio_kwargs(**params):
    return {}
