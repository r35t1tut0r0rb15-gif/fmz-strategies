"""A daily 07:00 UTC buy, 1-hour bars, long only: the bar opening at 07:00 goes long with a target one 5-minute ATR(14) above the signal close (its last value inside the hour); no stop.
Port of FMZ strategy #443038 "基于时间和ATR止损定时买入策略Time-based-ATR-Stop-Loss-Buy-Strategy" (Time-based Strategy with ATR Take Profit).

FMZ source id: 443038

Source
    https://www.fmz.com/strategy/443038 (PineScript v5, FMZ last modified 2024-02-28 17:36:50).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 144-190), trade time 0700; ATR 14 on 5 minutes; short side commented out
    hour * 100 + minute == 700 -> entry Buy, takeProfitLevel = close + atr5m;  exit(Take Profit BUY, limit = takeProfitLevel) every bar

Interpretation choices (Pine rules in SURVEY_README.md)
    * hour / minute are read on the UTC bar open, so the 07:00 bar signals once a day; a signal while
      long is refused (default pyramiding) but moves the script's target, which the port does not follow
      (as #439608). The 5-minute request from a 1-hour chart is a lower time frame: its value is the last
      5-minute bar inside the hour (as #436765), built from minutes in precompute. The target is
      tp_stop = ATR5 / close of the signal bar, shifted one bar inside stops() and re-based on the fill.
      There is no stop. Long only. Stop module: portfolio_kwargs {} (driver D4). No sizing code. FREQ =
      "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; target fixed at entry; the 5-minute value ends with the bar.
    2 generic: PASS, time-of-day entry with an ATR target.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: ND440364 (2 members, best partner #440364, Jaccard 0.750); ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: entries on the bar opening 07:00 UTC (bar open time).
Long only.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_443038_daily_0700_buy_5m_atr_target_long"
FAMILY = "calendar_seasonal"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "trade_hour": [7, 13],
    "atr_length": [14, 28],
}
DEFAULT_PARAMS = {"trade_hour": 7, "atr_length": 14}


def _resample(raw_1m_df, freq):
    ohlc = raw_1m_df[["open", "high", "low", "close"]]
    bars = ohlc.resample(freq, label="left", closed="left").agg(
        {"open": "first", "high": "max", "low": "min", "close": "last"})
    bars = bars.dropna(how="all")  # an empty period is not a bar; never forward-filled
    if bars.index.tz is None:
        raise ValueError("raw_1m_df must have a tz-aware UTC index")
    return bars


def _rma(x, n):
    """Wilder smoothing as Pine's rma: SMA seed over the first n valid values, then recursive."""
    v = x.to_numpy(dtype=float)
    out = np.full(v.shape, np.nan)
    valid = np.flatnonzero(~np.isnan(v))
    if len(valid) >= n:
        s = valid[0]
        out[s + n - 1] = v[s:s + n].mean()
        for i in range(s + n, len(v)):
            out[i] = (out[i - 1] * (n - 1) + v[i]) / n
    return pd.Series(out, index=x.index)


def precompute(raw_1m_df, symbol_key, **params):
    p = {**DEFAULT_PARAMS, **params}
    bars = _resample(raw_1m_df, FREQ)
    b5 = _resample(raw_1m_df, "5min")
    h, lo, c = b5["high"], b5["low"], b5["close"]
    pc = c.shift(1)
    tr = pd.concat([h - lo, (h - pc).abs(), (lo - pc).abs()], axis=1).max(axis=1)
    atr5 = _rma(tr, int(p["atr_length"]))
    last = atr5.groupby(b5.index.floor(FREQ)).last()          # the last 5-minute bar inside the hour
    bars["atr5"] = last.reindex(bars.index).to_numpy()
    return bars


def _tp(bars_df):
    return bars_df["atr5"] / bars_df["close"]


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    t = bars_df.index.tz_convert("UTC")
    go = (t.hour == int(p["trade_hour"])) & (t.minute == 0)
    tp = _tp(bars_df).to_numpy()
    ov, hv = bars_df["open"].to_numpy(dtype=float), bars_df["high"].to_numpy(dtype=float)
    m = len(ov)
    le = np.zeros(m, dtype=bool)
    pos, entry_i, t_ = 0, -1, np.nan
    for i in range(m):
        if pos == 1 and i >= entry_i and hv[i] >= ov[entry_i] * (1 + t_):
            pos = 0
        if pos == 0 and go[i] and i + 1 < m and not np.isnan(tp[i]):
            le[i], pos, entry_i, t_ = True, 1, i + 1, tp[i]
    ix = bars_df.index
    false = pd.Series(False, index=ix)
    return pd.Series(le, index=ix), false, false.copy(), false.copy()


def stops(bars_df, **params):
    return {"tp_stop": _tp(bars_df).shift(1)}


def portfolio_kwargs(**params):
    return {}
