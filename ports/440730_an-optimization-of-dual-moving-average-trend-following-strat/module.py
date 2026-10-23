"""Four-hour bars: the SMA 40 above the SMA 160 with the close above the SMA 40 and the low above the last completed day's parabolic SAR goes long; the mirror (high under that SAR) goes short; the opposite trend closes each, and each carries a stop 2 ATR 14 from the entry; reversing.
Port of FMZ strategy #440730 "An Optimization of Dual Moving Average Trend Following Strategy Based on Indicators Combination" (2 MA | Trend Following (sosacur01)).

FMZ source id: 440730

Source
    https://www.fmz.com/strategy/440730 (PineScript v5, FMZ last modified 2024-02-01 15:13:13).
    Verbatim copy: original_source.md. Read 2026-10-23 (FMZ-C).

Original signal (original_source.md lines 128-317), SMA 40 / 160; daily SAR 0.02 / 0.02 / 0.2 filter; ATR 14 x 2 stops; 2 % equity risk sizing
    long_entry = FASTMA > SLOWMA and close > FASTMA and low > security("D", sar(...));  long_exit = FASTMA < SLOWMA and close < FASTMA;  short mirror with high < psar
    sl := lastEntryPrice - 2 x atr(14) when the position changes;  exit("Long", stop = sl);  close("Long") when long_exit

Interpretation choices (Pine rules in SURVEY_README.md)
    * The daily SAR comes from security("D") without lookahead: the last completed broker day's value
      (the day's own value only on its last bar), computed on broker days built from the module's bars
      (as earlier ports). The stop is set on the bar the position changes, from the fill price and that
      bar's ATR, and sent from that bar's close; the house engine needs the distance at the fill, so the
      port uses the signal bar's ATR (2 x ATR[signal] / fill, as #434677) and arms it at the fill; the
      signals follow that stop, so a stopped position re-enters on the next qualifying bar, as Pine's
      repeated entry does. A close acts only on a position the bar's entries leave unchanged. The ATR risk sizing (2 % of equity) is
      sizing. Volume is not used (the MA types are SMA). REVERSAL INTENDED. Stop module: portfolio_kwargs
      {} (driver D4). Stops on 4-hour bars: mark coarse_bar_stop. FREQ = "4h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; ATR stop from the signal bar as a fraction of the fill.
    2 generic: PASS, dual-SMA trend with a daily SAR filter.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: qty = equity x 2 % / (2 x ATR), commission 0.2 %, not ported.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: last completed broker day (17:00 America/New_York) for the SAR.
REVERSAL INTENDED.

Marks: coarse_bar_stop
"""
import numpy as np
import pandas as pd

NAME = "fmz_440730_sma40_160_trend_daily_sar_filter_atr_stop_4h_reversal"
FAMILY = "ma_state"  # proposed 2026-10-23 (FMZ-C), user to confirm
FREQ = "4h"  # backtest header period: 4h
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "fast": [40, 20],
    "slow": [160, 100],
}
DEFAULT_PARAMS = {"fast": 40, "slow": 160, "sar_start": 0.02, "sar_inc": 0.02, "sar_max": 0.2, "atr_len": 14,
                  "sl_mult": 2.0}


def _resample(raw_1m_df, freq):
    ohlcv = raw_1m_df[["open", "high", "low", "close", "volume"]]
    bars = ohlcv.resample(freq, label="left", closed="left").agg(
        {"open": "first", "high": "max", "low": "min", "close": "last", "volume": "sum"})
    bars = bars.dropna(subset=["close"])  # an empty period is not a bar; never forward-filled
    if bars.index.tz is None:
        raise ValueError("raw_1m_df must have a tz-aware UTC index")
    return bars


def precompute(raw_1m_df, symbol_key, **params):
    return _resample(raw_1m_df, FREQ)


def broker_day(index):
    """Broker day of each timestamp: the session ending 17:00 America/New_York, labelled by its
    end date (as worker A's ports). The desktop binds this name to registry_schema.broker_day."""
    ny = index.tz_convert("America/New_York")
    return (ny + pd.Timedelta(hours=7)).normalize().tz_localize(None)


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
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    fast, slow = c.rolling(int(p["fast"])).mean(), c.rolling(int(p["slow"])).mean()
    day = broker_day(c.index)
    dh, dl, dc = h.groupby(day).max(), lo.groupby(day).min(), c.groupby(day).last()
    dsar = pd.Series(_sar(dh.to_numpy(dtype=float), dl.to_numpy(dtype=float), dc.to_numpy(dtype=float),
                          float(p["sar_start"]), float(p["sar_inc"]), float(p["sar_max"])), index=dc.index).shift(1)
    psar = pd.Series(dsar.reindex(day).to_numpy(), index=c.index)   # the last COMPLETED broker day
    bull = (fast > slow) & (c > fast)
    bear = (fast < slow) & (c < fast)
    lg = (bull & (lo > psar)).to_numpy()
    sh = (bear & (h < psar)).to_numpy()
    bu, be = bull.to_numpy(), bear.to_numpy()
    pc = c.shift(1)
    tr = pd.concat([h - lo, (h - pc).abs(), (lo - pc).abs()], axis=1).max(axis=1).where(pc.notna())
    dist = (float(p["sl_mult"]) * _rma(tr, int(p["atr_len"]))).to_numpy()
    ov, hv, lv = (bars_df[k].to_numpy(dtype=float) for k in ("open", "high", "low"))
    m = len(lg)
    le, lx = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    se, sx = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    tgt, lvl = 0, np.nan
    for i in range(m):
        if i > 0 and le[i - 1]:
            lvl = ov[i] - dist[i - 1]                  # the stop the engine arms at this fill
        elif i > 0 and se[i - 1]:
            lvl = ov[i] + dist[i - 1]
        if tgt == 1 and lv[i] <= lvl:                  # stopped inside the bar: flat, entries may follow
            tgt = 0
        elif tgt == -1 and hv[i] >= lvl:
            tgt = 0
        pos = tgt
        new = pos
        if lg[i] and new != 1:
            new = 1
        if sh[i] and new != -1:
            new = -1
        if new == pos:
            if pos == 1 and be[i]:
                new = 0
            elif pos == -1 and bu[i]:
                new = 0
        if new != pos and i + 1 < m:
            if new == 1:
                le[i] = True
            elif new == -1:
                se[i] = True
            elif pos == 1:
                lx[i] = True
            else:
                sx[i] = True
            tgt = new
    ix = bars_df.index
    return (pd.Series(le, index=ix), pd.Series(lx, index=ix),
            pd.Series(se, index=ix), pd.Series(sx, index=ix))


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    h, lo, c, o = bars_df["high"], bars_df["low"], bars_df["close"], bars_df["open"]
    pc = c.shift(1)
    tr = pd.concat([h - lo, (h - pc).abs(), (lo - pc).abs()], axis=1).max(axis=1).where(pc.notna())
    atr = _rma(tr, int(p["atr_len"]))
    return {"sl_stop": (float(p["sl_mult"]) * atr).shift(1) / o}


def portfolio_kwargs(**params):
    return {}
