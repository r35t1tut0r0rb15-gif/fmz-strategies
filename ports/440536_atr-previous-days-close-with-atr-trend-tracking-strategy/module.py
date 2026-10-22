"""Daily close plus ATR breakouts, 1-hour bars: a close more than 0.8 daily ATR(14) above the daily reference close (but under the reference low plus 1.7 ATR) goes long, with a stop 0.2 ATR above the
reference close and a target at the reference low plus 1.7 ATR; mirrored for shorts; reversing.
Port of FMZ strategy #440536 "基于前一天收盘价和ATR指标的趋势追踪策略Previous-Days-Close-with-ATR-Trend-Tracking-Strategy" (PC_ATR).

FMZ source id: 440536

Source
    https://www.fmz.com/strategy/440536 (PineScript v3, FMZ last modified 2024-01-31 14:39:09).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 158-205), ATR 14 on D; entry 0.8, target 1.7, stop 0.2 ATR; size 10; start year 2014
    ATR = security('D', atr(14));  yesterday = security('D', close[1]);  dl / dh = security('D', low[1] / high[1]);  TPup = yesterday + 0.8 ATR;  profitlevelup = dl + 1.7 ATR;  slup = yesterday + 0.2 ATR
    close > TPup and close < profitlevelup -> entry LONG, strategy.exit(stop = slup, limit = profitlevelup);  mirrored for SHORT (sldown, profitleveldown = dh - 1.7 ATR)

Interpretation choices (Pine rules in SURVEY_README.md)
    * A version-3 security() without lookahead is read as the last completed higher bar: the daily ATR
      is that of the last completed broker day, and the [1] references are one day before it (the
      close, low and high of two broker days back), built from the module's own bars, as written. The
      levels are set on the signal bar: sl_stop and tp_stop are their distances from the signal close,
      shifted one bar inside stops() and re-based on the fill; a later same-direction signal only moves
      the script's levels, which the port does not follow. The OCA name and the year filter do not
      change the orders. strategy.entry reverses: REVERSAL INTENDED. Stop module: portfolio_kwargs {}
      (driver D4). The size 10 is sizing. FREQ = "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; daily values from completed days; bracket fixed at entry.
    2 generic: PASS, daily close, range and ATR levels.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: size 10 is sizing.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: broker day for the daily values (17:00 America/New_York, DST by the zone).
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_440536_prev_close_daily_atr_breakout"
FAMILY = "atr_band_breakout"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "entr": [0.8, 0.5],
    "tplevel": [1.7, 2.5],
}
DEFAULT_PARAMS = {"entr": 0.8, "tplevel": 1.7, "sl": 0.2, "atr_len": 14}


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


def _setup(bars_df, p):
    c = bars_df["close"]
    day = broker_day(bars_df.index)
    d = bars_df.groupby(day).agg({"high": "max", "low": "min", "close": "last"})
    pc = d["close"].shift(1)
    tr = pd.concat([d["high"] - d["low"], (d["high"] - pc).abs(), (d["low"] - pc).abs()], axis=1).max(axis=1)
    atr_d = _rma(tr, int(p["atr_len"]))

    def onbars(x, k):
        return pd.Series(x.shift(k).reindex(day).to_numpy(), index=c.index)

    atr = onbars(atr_d, 1)                               # last completed day
    yc, dl, dh = onbars(d["close"], 2), onbars(d["low"], 2), onbars(d["high"], 2)
    e, t, s = float(p["entr"]), float(p["tplevel"]), float(p["sl"])
    lsig = (c > yc + e * atr) & (c < dl + t * atr)
    ssig = (c < yc - e * atr) & (c > dh - t * atr)
    sl = ((c - (yc + s * atr)) / c).where(lsig, ((yc - s * atr - c) / c).where(ssig))
    tp = ((dl + t * atr - c) / c).where(lsig, ((c - (dh - t * atr)) / c).where(ssig))
    ok = (sl > 0) & (tp > 0)
    return lsig.to_numpy() & ok.to_numpy(), ssig.to_numpy() & ok.to_numpy(), sl.where(ok), tp.where(ok)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    lsig, ssig, sl_s, tp_s = _setup(bars_df, p)
    sl, tp = sl_s.to_numpy(), tp_s.to_numpy()
    ov = bars_df["open"].to_numpy(dtype=float)
    hv, lv = bars_df["high"].to_numpy(dtype=float), bars_df["low"].to_numpy(dtype=float)
    m = len(ov)
    le, se = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    pos, entry_i, s_, t_ = 0, -1, np.nan, np.nan
    for i in range(m):
        if pos != 0 and i >= entry_i:
            x = ov[entry_i]
            if pos == 1 and (lv[i] <= x * (1 - s_) or hv[i] >= x * (1 + t_)):
                pos = 0
            elif pos == -1 and (hv[i] >= x * (1 + s_) or lv[i] <= x * (1 - t_)):
                pos = 0
        if i + 1 < m:
            if lsig[i] and pos != 1:
                le[i], pos, entry_i, s_, t_ = True, 1, i + 1, sl[i], tp[i]
            elif ssig[i] and pos != -1:
                se[i], pos, entry_i, s_, t_ = True, -1, i + 1, sl[i], tp[i]
    ix = bars_df.index
    false = pd.Series(False, index=ix)
    return pd.Series(le, index=ix), false, pd.Series(se, index=ix), false.copy()


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    _, _, sl, tp = _setup(bars_df, p)
    return {"sl_stop": sl.shift(1), "tp_stop": tp.shift(1)}


def portfolio_kwargs(**params):
    return {}
