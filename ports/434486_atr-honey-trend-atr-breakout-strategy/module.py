"""Daily pivot +/- half a daily ATR with a DTI trend filter, 1-hour bars, entries from flat: a bar touching the lower band
(low or open at or under it) and closing above it, with ATR 3 above ATR 50 and the DTI signal rising over 3 bars, goes
long, closed when a high passes the pivot; the upper-band mirror goes short, closed when a low passes under the pivot.
Each trade carries a stop of 100 ticks, re-expressed as an ATR multiple.
Port of FMZ strategy #434486 "趋势ATR横向突破策略Honey-Trend-ATR-Breakout-Strategy" (Strategy - Bobo PATR Swing).

FMZ source id: 434486

Source
    https://www.fmz.com/strategy/434486 (PineScript v2, FMZ last modified 2023-12-06 18:03:38).
    Verbatim copy: original_source.md. Read 2026-10-17 (FMZ-C).

Original signal (original_source.md lines 187-244), pivot and ATR timeframe D, ATR 13, divisor 2; DTI 2 / 20 / 5 / 3, signal 4; TP 0 (off), SL 100 ticks
    pivot = security('D', (high[1] + low[1] + close[1]) / 3);  datr = security('D', atr(13)[1]);  bands = pivot -/+ datr / 2
    enterLong = (low <= lb and close > lb or open <= lb and close > lb) and opentrades < 1 and atr(3) > atr(50) and signal > signal[3];  exitLong = high > pivot
    shorts mirror (high / open >= ub, close < ub, signal < signal[3], exit low < pivot);  exit(loss = 100) both sides

Interpretation choices (Pine rules in SURVEY_README.md)
    * Both security values carry [1] inside the daily series: the last completed broker day's
      typical price and its Wilder ATR 13 of broker days (17:00 America/New_York), built from the
      port's own bars, known from the next day's first bar.
    * Criterion 2: 100 ticks of 0.1 on hourly BTC (10 USD) are about 0.05 x the hourly Wilder ATR 13
      of the signal bar (sl_atr, a fraction of the signal close shifted one bar inside stops(),
      re-based on the fill). The take profit is 0 (off).
    * Entries only from flat (opentrades < 1): "flat" follows the house stop on bars and the exit
      signals. The exits act on the position held on the bar (high / low against the pivot, close
      based). Opposite entries cannot occur. Stop module: portfolio_kwargs {} (driver D4). FREQ =
      "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; stop fixed at entry.
    2 generic: ADAPT, tick stop -> ATR multiple; pivot bands from prior broker days.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: the fixed quantity 1 and the capital stored.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: ND434486 (2 members, best partner #436614, Jaccard 0.710); ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: daily pivot and ATR on broker days (17:00 America/New_York, DST by the zone); no venue-open rule.
Opposite entries cannot occur.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_434486_daily_pivot_atr_band_dti"
FAMILY = "pivot_reversal"  # proposed 2026-10-17 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "atrdiv": [2.0, 1.0],
    "sl_atr": [0.05, 1.0],
}
DEFAULT_PARAMS = {"atr_len": 13, "atrdiv": 2.0, "i1": 2, "i2": 20, "i3": 5, "i4": 3, "i5": 4, "sl_atr": 0.05}


def broker_day(index):
    """Broker day of each timestamp: the session ending 17:00 America/New_York, labelled by its
    end date (as worker A's ports). The desktop binds this name to registry_schema.broker_day."""
    ny = index.tz_convert("America/New_York")
    return (ny + pd.Timedelta(hours=7)).normalize().tz_localize(None)


def _resample(raw_1m_df, freq):
    ohlc = raw_1m_df[["open", "high", "low", "close"]]
    bars = ohlc.resample(freq, label="left", closed="left").agg(
        {"open": "first", "high": "max", "low": "min", "close": "last"})
    bars = bars.dropna(how="all")  # an empty period is not a bar; never forward-filled
    if bars.index.tz is None:
        raise ValueError("raw_1m_df must have a tz-aware UTC index")
    return bars


def _tr(h, lo, c):
    c1 = c.shift(1)
    return pd.concat([h - lo, (h - c1).abs(), (lo - c1).abs()], axis=1).max(axis=1)


def _prev_day(bars_df, n):
    """Typical price and Wilder ATR n of the last completed broker day, on every bar of the next."""
    day = broker_day(bars_df.index)
    g = pd.DataFrame({k: bars_df[k].to_numpy() for k in ("high", "low", "close")}, index=day)
    d = g.groupby(level=0).agg({"high": "max", "low": "min", "close": "last"})
    tr = _tr(d["high"], d["low"], d["close"])
    tr.iloc[0] = np.nan
    atr = tr.ewm(alpha=1 / n, adjust=False).mean()
    piv = ((d["high"] + d["low"] + d["close"]) / 3).shift(1)
    return piv.reindex(day).to_numpy(), atr.shift(1).reindex(day).to_numpy()


def _setup(bars_df, p):
    o, h, lo, c = (bars_df[k] for k in ("open", "high", "low", "close"))
    piv, datr = _prev_day(bars_df, int(p["atr_len"]))
    ub, lb = piv + datr / float(p["atrdiv"]), piv - datr / float(p["atrdiv"])
    hd, ld = h.diff(), -lo.diff()
    udm = pd.Series(np.where((hd > ld) & (hd > 0), hd, 0.0), index=c.index)
    ddm = pd.Series(np.where((ld > hd) & (ld > 0), ld, 0.0), index=c.index)
    i1 = int(p["i1"])
    rma = lambda x, n: x.ewm(alpha=1 / n, adjust=False).mean()  # noqa: E731
    tr_t = _tr(h, lo, c)                      # tr(true): high - low on the first bar
    atr_i = rma(tr_t, i1)
    hlm = 100 * rma(udm, i1) / atr_i - 100 * rma(ddm, i1) / atr_i
    e3 = lambda x: (x.ewm(span=int(p["i2"]), adjust=False).mean()  # noqa: E731
                    .ewm(span=int(p["i3"]), adjust=False).mean().ewm(span=int(p["i4"]), adjust=False).mean())
    dti = 100 * e3(hlm) / e3(hlm.abs())
    sig = dti.ewm(span=int(p["i5"]), adjust=False).mean()
    tr_f = _tr(h, lo, c)
    tr_f.iloc[0] = np.nan
    vol_ok = rma(tr_f, 3) > rma(tr_f, 50)
    ov, hv, lv, cv = (x.to_numpy(dtype=float) for x in (o, h, lo, c))
    with np.errstate(invalid="ignore"):
        en_l = (((lv <= lb) & (cv > lb)) | ((ov <= lb) & (cv > lb))) & vol_ok.to_numpy() & \
            (sig > sig.shift(3)).to_numpy()
        en_s = (((hv >= ub) & (cv < ub)) | ((ov >= ub) & (cv < ub))) & vol_ok.to_numpy() & \
            (sig < sig.shift(3)).to_numpy()
        ex_l, ex_s = hv > piv, lv < piv
    frac = float(p["sl_atr"]) * rma(tr_f, int(p["atr_len"])).to_numpy() / cv
    return en_l, en_s, ex_l, ex_s, frac


def _run(bars_df, p):
    en_l, en_s, ex_l, ex_s, frac = _setup(bars_df, p)
    ov, hv, lv = (bars_df[k].to_numpy(dtype=float) for k in ("open", "high", "low"))
    m = len(ov)
    le, lx, se, sx = (np.zeros(m, dtype=bool) for _ in range(4))
    sl = np.full(m, np.nan)
    pos, ei, s_ = 0, -1, np.nan
    for i in range(m):
        if pos != 0 and i >= ei and not np.isnan(s_):        # the house stop from the fill price
            e = ov[ei]
            if (pos == 1 and lv[i] <= e * (1 - s_)) or (pos == -1 and hv[i] >= e * (1 + s_)):
                pos = 0
        nxt = pos
        if pos == 1 and i >= ei and ex_l[i]:
            lx[i], nxt = True, 0
        elif pos == -1 and i >= ei and ex_s[i]:
            sx[i], nxt = True, 0
        if pos == 0 and en_l[i]:
            le[i], nxt, ei, s_ = True, 1, i + 1, frac[i]
            sl[i] = s_
        elif pos == 0 and en_s[i]:
            se[i], nxt, ei, s_ = True, -1, i + 1, frac[i]
            sl[i] = s_
        pos = nxt
    return le, lx, se, sx, sl


def precompute(raw_1m_df, symbol_key, **params):
    return _resample(raw_1m_df, FREQ)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    le, lx, se, sx, _ = _run(bars_df, p)
    ix = bars_df.index
    return pd.Series(le, index=ix), pd.Series(lx, index=ix), pd.Series(se, index=ix), pd.Series(sx, index=ix)


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    *_, sl = _run(bars_df, p)
    return {"sl_stop": pd.Series(sl, index=bars_df.index).shift(1)}


def portfolio_kwargs(**params):
    return {}
