"""Buying runs of 3 to 5 red candles above the SMA 200, daily bars, long only: each trade has a 0.5 % target and 0.5 % stop, and also closes on the close crossing under the parabolic SAR (that bar or the one before), on the close crossing back over the SMA 5, or on a doji.
Port of FMZ strategy #468299 "Multi Indicator Synergy Long Term Trading Strategy" (Estrategia Long con 3 Velas Rojas y SL/TP + Parabolic SAR, Media Móvil y Doji).

FMZ source id: 468299

Source
    https://www.fmz.com/strategy/468299 (PineScript v5, FMZ last modified 2024-09-26 14:32:13).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 183-261), red-candle count 3 to open, under 6 allowed; SMA 200; stop / target 0.5 % of the signal close; SAR 0.02 / 0.02 / 0.2; SMA 5 exit; doji = body <= 10 % of the range
    red count >= 3 and < 6 and close > sma200 -> entry Compra + exit(limit = close x 1.005, stop = close x 0.995)
    long: crossunder(close, sar)[1] -> close;  else crossunder(close, sar) -> close;  close[1] < sma5[1] and close > sma5 -> close;  doji -> close

Interpretation choices (Pine rules in SURVEY_README.md)
    * The bracket is sent on the signal bar from its close: ported as the fixed fraction 0.005 of the
      fill. A further red candle while held re-sends it from the new close, which stops() cannot
      express: the opening levels are kept (as #434428, mark trailing_stop_pending). The bracket is
      followed in the loop so the closes and the next entries line up (the closes act only on a long
      still held at the bar's close). The SMA 5 exit is a cross back up, as written. Pine's ta.sar as
      documented. Long only. Stop module: portfolio_kwargs {} (driver D4). Stops on daily bars: mark
      coarse_bar_stop. No sizing code. FREQ = "1D" from the backtest header (broker days).

Admission criteria
    1 fits the interface: PASS, bar-close orders; the percent bracket as fixed fractions.
    2 generic: PASS, red-candle dips in an uptrend with SAR, SMA and doji exits.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (8 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
Long only.

Marks: coarse_bar_stop, trailing_stop_pending
"""
import numpy as np
import pandas as pd

NAME = "fmz_468299_red_candle_run_dip_sma200_sar_sma5_doji_exits_long"
FAMILY = "candle_pattern"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "open_count": [3, 2],
    "bracket": [0.005, 0.02],
    "ma_len": [200, 100],
}
DEFAULT_PARAMS = {"open_count": 3, "limit_count": 6, "bracket": 0.005, "ma_len": 200, "exit_len": 5}


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


def _sar(hv, lv, cv, start, inc, mx):
    """Pine's ta.sar as documented (pine_sar)."""
    m = len(cv)
    out = np.full(m, np.nan)
    res = mm = acc = np.nan
    below = None
    for i in range(1, m):
        first = False
        if i == 1:
            if cv[1] > cv[0]:
                below, mm, res = True, hv[1], lv[0]
            else:
                below, mm, res = False, lv[1], hv[0]
            first, acc = True, start
        res = res + acc * (mm - res)
        if below:
            if res > lv[i]:
                first, below = True, False
                res, mm, acc = max(hv[i], mm), lv[i], start
        else:
            if res < hv[i]:
                first, below = True, True
                res, mm, acc = min(lv[i], mm), hv[i], start
        if not first:
            if below:
                if hv[i] > mm:
                    mm, acc = hv[i], min(acc + inc, mx)
            else:
                if lv[i] < mm:
                    mm, acc = lv[i], min(acc + inc, mx)
        if below:
            res = min(res, lv[i - 1])
            if i > 1:
                res = min(res, lv[i - 2])
        else:
            res = max(res, hv[i - 1])
            if i > 1:
                res = max(res, hv[i - 2])
        out[i] = res
    return out


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    o, h, lo, c = (bars_df[k] for k in ("open", "high", "low", "close"))
    ov, hv, lv, cv = (x.to_numpy(dtype=float) for x in (o, h, lo, c))
    m = len(cv)
    red = cv < ov
    cnt = np.zeros(m, dtype=int)
    for i in range(m):
        cnt[i] = cnt[i - 1] + 1 if (red[i] and i > 0) else (1 if red[i] else 0)
    ma = c.rolling(int(p["ma_len"])).mean().to_numpy()
    with np.errstate(invalid="ignore"):
        go = (cnt >= int(p["open_count"])) & (cnt < int(p["limit_count"])) & (cv > ma)
    sar = pd.Series(_sar(hv, lv, cv, 0.02, 0.02, 0.2), index=c.index)
    sdn = (c < sar) & (c.shift(1) >= sar.shift(1))
    mx = c.rolling(int(p["exit_len"])).mean()
    out = (sdn.shift(1, fill_value=False) | sdn | ((c.shift(1) < mx.shift(1)) & (c > mx))
           | ((o - c).abs() <= (h - lo) * 0.1)).to_numpy()
    b = float(p["bracket"])
    le, lx = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    pos, pend, sl, tp = 0, 0, np.nan, np.nan
    for i in range(m):
        if pend == 1:
            pos, sl, tp = 1, ov[i] * (1 - b), ov[i] * (1 + b)
        elif pend == 2:
            pos = 0
        pend = 0
        if pos == 1 and (lv[i] <= sl or hv[i] >= tp):
            pos = 0                              # the bracket fills inside this bar
        if go[i] and pos == 0:
            le[i], pend = True, 1
        elif pos == 1 and out[i]:
            lx[i], pend = True, 2
    ix = bars_df.index
    false = pd.Series(False, index=ix)
    return pd.Series(le, index=ix), pd.Series(lx, index=ix), false, false.copy()


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    b = float(p["bracket"])
    return {"sl_stop": b, "tp_stop": b}


def portfolio_kwargs(**params):
    return {}
