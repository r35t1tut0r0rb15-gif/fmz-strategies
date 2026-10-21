"""MACD histogram, RSI, EMA 8 / 21 and an ATR distance, broker days, long only: from flat, the histogram above 0, the RSI 14 above 50, the EMA 8 above the EMA 21 and the close more than 2 ATR(20) above the EMA 21
buys; a negative histogram with the EMA 8 under the EMA 21, a close 9 % under the highest close since the last entry-condition bar, or a close with close x 0.85 above the entry price closes it.
Port of FMZ strategy #437795 "均线黄金交叉RSI-MACD策略Improved-RSI-MACD-Moving-Average-Strategy" (Improved RSI MACD Strategy with Moving Averages).

FMZ source id: 437795

Source
    https://www.fmz.com/strategy/437795 (PineScript v5, FMZ last modified 2024-01-05 16:11:23).
    Verbatim copy: original_source.md. Read 2026-10-21 (FMZ-C).

Original signal (original_source.md lines 164-229), RSI 14 on close; stop 0.09, target 0.15; MACD 12 / 26 / 9; entry and exit levels 0; EMA 8 / 21; ATR 20 x 2
    longCondition = hist > 0 and rsi > 50 and ema 8 > ema 21 and close > ema 21 + 2 ATR -> entry Long, lastEntryPrice := close;  lastEntryPrice := max(it, close) on every bar
    hist < 0 and ema 8 < ema 21 -> close Long;  long and close < lastEntryPrice x (1 - 0.09) -> close;  long and close x (1 - 0.15) > entry price -> close

Interpretation choices (Pine rules in SURVEY_README.md)
    * lastEntryPrice is reset to the close on every bar of the entry condition (not only at fills) and
      rises with each higher close, so the stop is a close-tested 9 % trail from the highest close since
      the last condition bar. All three exits are close tests that fill at the next open (no broker
      stop). The take-profit test is as written: close x 0.85 above the entry price, a gain above 17.6 %
      (owed: probably close > entry x 1.15). Closes act on the position open at the bar close; the entry
      only from flat. Long only. No sizing code. Daily bars are broker days (17:00 America/New_York),
      stamped with their first minute. FREQ = "1D" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; close-tested exits.
    2 generic: PASS, MACD, RSI, EMAs and ATR.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: broker day (17:00 America/New_York, DST by the zone); no venue-open rule.
Long only.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_437795_rsi_macd_ema_atr_long"
FAMILY = "multi_indicator_confluence"  # proposed 2026-10-21 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "stop_pct": [0.09, 0.05],
    "atr_mult": [2.0, 1.0],
}
DEFAULT_PARAMS = {"stop_pct": 0.09, "atr_mult": 2.0, "take_pct": 0.15, "rsi_len": 14, "fast": 12, "slow": 26,
                  "signal": 9, "ema_short": 8, "ema_long": 21, "atr_len": 20}


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


def _rsi(c, n):
    d = c.diff()
    up = _rma(d.clip(lower=0), n)
    dn = _rma((-d).clip(lower=0), n)
    with np.errstate(divide="ignore", invalid="ignore"):
        r = 100.0 - 100.0 / (1.0 + up / dn)
    r = r.where(up != 0, 0.0).where(dn != 0, 100.0)    # Pine: down == 0 -> 100, else up == 0 -> 0
    return r.where(up.notna() & dn.notna())


def _atr(bars_df, n):
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    pc = c.shift(1)
    tr = pd.concat([h - lo, (h - pc).abs(), (lo - pc).abs()], axis=1).max(axis=1)
    return _rma(tr, int(n))


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    o, c = bars_df["open"], bars_df["close"]
    r = _rsi(c, int(p["rsi_len"]))
    macd = c.ewm(span=int(p["fast"]), adjust=False).mean() - c.ewm(span=int(p["slow"]), adjust=False).mean()
    hist = macd - macd.ewm(span=int(p["signal"]), adjust=False).mean()
    es = c.ewm(span=int(p["ema_short"]), adjust=False).mean()
    el = c.ewm(span=int(p["ema_long"]), adjust=False).mean()
    atr = _atr(bars_df, p["atr_len"])
    lc = ((hist > 0) & (r > 50) & (es > el) & (c > el + float(p["atr_mult"]) * atr)).to_numpy()
    ex1 = ((hist < 0) & (es < el)).to_numpy()
    ov, cv = o.to_numpy(dtype=float), c.to_numpy(dtype=float)
    sl, tp = float(p["stop_pct"]), float(p["take_pct"])
    m = len(cv)
    le, lx = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    pos, entry_px, peak = 0, np.nan, np.nan
    pend_e = pend_x = False
    for i in range(m):
        if pend_x:                                       # orders of the last bar fill at this open
            pos, pend_x = 0, False
        if pend_e:
            pos, entry_px, pend_e = 1, ov[i], False
        if lc[i]:
            peak = cv[i]
        if peak < cv[i]:
            peak = cv[i]
        if pos == 1:
            if ex1[i] or cv[i] < peak * (1 - sl) or cv[i] * (1 - tp) > entry_px:
                lx[i], pend_x = True, True
        elif lc[i] and i + 1 < m:
            le[i], pend_e = True, True
    ix = bars_df.index
    false = pd.Series(False, index=ix)
    return pd.Series(le, index=ix), pd.Series(lx, index=ix), false, false.copy()


def portfolio_kwargs(**params):
    return {}
