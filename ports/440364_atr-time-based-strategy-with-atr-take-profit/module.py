"""Daily 07:00 UTC short with a 5-minute-ATR target, 1-hour bars, short only: the bar opening at 07:00 UTC goes short, with a target one 5-minute ATR(14) below the entry; no stop.
Port of FMZ strategy #440364 "基于时间和ATR指标的止损止盈策略Time-based-Strategy-with-ATR-Take-Profit" (Time-based Strategy with ATR Take Profit Sell).

FMZ source id: 440364

Source
    https://www.fmz.com/strategy/440364 (PineScript v5, FMZ last modified 2024-01-29 16:13:57).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 152-195), trade time 0700 (HHMM); ATR 14 on 5-minute bars; the buy side commented out
    sellCondition = hour x 100 + minute == 700 -> entry Sell, sellprice = close, takeProfitLevelForSell = close - atrValue;  every bar: strategy.exit(limit = takeProfitLevelForSell)
    atrValue = request.security(syminfo.tickerid, "5", ta.atr(14))

Interpretation choices (Pine rules in SURVEY_README.md)
    * hour and minute are read on the UTC bar open: on 1-hour bars the 07:00 bar. The 5-minute ATR
      requested from the 1-hour chart is the last 5-minute bar inside the chart bar (a lower time frame
      returns its last bar, as #436765), built from the loader's minutes. The target is set from the
      signal close: tp_stop = 5-minute ATR / close of the signal bar, shifted one bar inside stops() and
      re-based on the fill; a later 07:00 signal while still short only moves the script's target,
      which the port does not follow. The buy side is commented out: Short only: Opposite entries
      cannot occur. Stop module: portfolio_kwargs {} (driver D4). No sizing code. FREQ = "1h" from the
      backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; target fixed at entry; the 5-minute value ends with the chart bar.
    2 generic: PASS, time of day and a 5-minute ATR.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: ND440364 (2 members, best partner #443038, Jaccard 0.750); ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: entries on the bar opening 07:00 UTC (bar open time).
Short only: Opposite entries cannot occur.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_440364_0700_short_5min_atr_target"
FAMILY = "calendar_seasonal"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "trade_hour": [7, 13],
    "atr_len": [14, 28],
}
DEFAULT_PARAMS = {"trade_hour": 7, "atr_len": 14, "ltf": "5min"}


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
    b5 = _resample(raw_1m_df, p["ltf"])
    pc = b5["close"].shift(1)
    tr = pd.concat([b5["high"] - b5["low"], (b5["high"] - pc).abs(), (b5["low"] - pc).abs()], axis=1).max(axis=1)
    atr5 = _rma(tr, int(p["atr_len"]))
    lab = b5.index.floor(FREQ)
    last = ~pd.Index(lab).duplicated(keep="last")         # the last 5-minute bar inside each 1-hour bar
    a = pd.Series(atr5.to_numpy()[last], index=lab[last])
    bars["atr5"] = a.reindex(bars.index).to_numpy()
    return bars


def _setup(bars_df, p):
    ix = bars_df.index.tz_convert("UTC")
    sig = (ix.hour == int(p["trade_hour"])) & (ix.minute == 0)
    tp = (bars_df["atr5"] / bars_df["close"]).where(sig)
    return tp


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    tp = _setup(bars_df, p).to_numpy()
    ov = bars_df["open"].to_numpy(dtype=float)
    lv = bars_df["low"].to_numpy(dtype=float)
    m = len(ov)
    se = np.zeros(m, dtype=bool)
    pos, entry_i, t_ = 0, -1, np.nan
    for i in range(m):
        if pos == -1 and i >= entry_i and lv[i] <= ov[entry_i] * (1 - t_):
            pos = 0
        if pos == 0 and i + 1 < m and not np.isnan(tp[i]):
            se[i], pos, entry_i, t_ = True, -1, i + 1, tp[i]
    ix = bars_df.index
    false = pd.Series(False, index=ix)
    return false, false.copy(), pd.Series(se, index=ix), false.copy()


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    return {"tp_stop": _setup(bars_df, p).shift(1)}


def portfolio_kwargs(**params):
    return {}
