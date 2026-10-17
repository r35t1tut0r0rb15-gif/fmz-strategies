"""EMA 3 / RMA 3 ATR channel breakouts from flat with the signal bar's open as the stop, broker days: a close above
EMA 3 + 1.5 ATR(3) or RMA 3 + 1 ATR(3) goes long when flat, stopped at the signal bar's open; the mirror goes short;
the low crossing above the previous bar's open closes the long, the high crossing below it closes the short.
Port of FMZ strategy #489654 "三重指数移动平均与三重相对移动平均自适应通道交叉策略-Triple-EMA-and-Triple-RMA-Adaptive-Channel-Crossover-Strategy" (EMA3 & RMA3 ATR Strategy).

FMZ source id: 489654

Source
    https://www.fmz.com/strategy/489654 (PineScript v5, FMZ last modified 2025-04-07 13:43:30).
    Verbatim copy: original_source.md. Read 2026-10-17 (FMZ-C laptop lane).

Original signal (original_source.md lines 231-287), EMA 3 x 1.5 ATR, RMA 3 x 1.0 ATR, ATR 3, risk 0.5 %
    buy = close > ema3 + 1.5 ATR or close > rma3 + 1 ATR;  sell = close < ema3 - 1.5 ATR or close < rma3 - 1 ATR
    flat and buy -> entry long (risk-based qty) + exit(stop = open);  flat and sell -> short, stop = open
    long held: crossover(low, prev_open) -> close;  short held: crossunder(high, prev_open) -> close (prev_open = open[1])

Interpretation choices (Pine rules in SURVEY_README.md)
    * The stop is the signal bar's open: sl_stop = (close - open) / close for a long (mirror for a short), shifted one
      bar inside stops(), re-based on the fill. A signal bar that closes on the wrong side of its open would be
      stopped at once on the fill (and its risk-based quantity is na when they are equal): no entry is emitted.
    * Entries only from flat: simulate() follows the house stop on bars (from the fill bar), as the desktop's
      flat-only bracket ports; the closes are close-checked signals. A buy wins over a sell on one bar (source order).
      Opposite entries cannot occur.
    * Stop module: portfolio_kwargs {} (D4). Daily bars are broker days (17:00 America/New_York), stamped with their
      first minute; FREQ = "1D" from the backtest header: coarse_bar_stop.

Admission criteria
    1 fits the interface: PASS, bar-close orders; stop fixed at the signal bar.
    2 generic: PASS, ATR channels and bar levels.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: the 0.5 %-risk quantity quoted; the stop ported via stops() and quoted in original_sizing.txt.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: broker day (17:00 America/New_York, DST by the zone); no venue-open rule.
Opposite entries cannot occur.

Marks: coarse_bar_stop
"""
import numpy as np
import pandas as pd

NAME = "fmz_489654_ema3_rma3_atr_channel_open_stop"
FAMILY = "atr_band_breakout"  # proposed 2026-10-17 (FMZ-C laptop lane), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "ema_mult": [1.5, 2.5],
    "rma_mult": [1.0, 2.0],
}
DEFAULT_PARAMS = {"ema_len": 3, "ema_mult": 1.5, "rma_len": 3, "rma_mult": 1.0, "atr_len": 3}


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


def _atr(bars_df, n):
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    pc = c.shift(1)
    tr = pd.concat([h - lo, (h - pc).abs(), (lo - pc).abs()], axis=1).max(axis=1, skipna=False)
    tr.iloc[0] = h.iloc[0] - lo.iloc[0]   # Pine's first true range is high - low
    return _rma(tr, n)


def _run(bars_df, p):
    o, h, lo, c = (bars_df[k] for k in ("open", "high", "low", "close"))
    atr = _atr(bars_df, int(p["atr_len"]))
    ema = c.ewm(span=int(p["ema_len"]), adjust=False).mean()
    rma = _rma(c, int(p["rma_len"]))
    buy = ((c > ema + atr * p["ema_mult"]) | (c > rma + atr * p["rma_mult"])).to_numpy()
    sell = ((c < ema - atr * p["ema_mult"]) | (c < rma - atr * p["rma_mult"])).to_numpy()
    po = o.shift(1)
    x_long = ((lo > po) & (lo.shift(1) <= po.shift(1))).to_numpy()
    x_short = ((h < po) & (h.shift(1) >= po.shift(1))).to_numpy()
    ov, hv, lv, cv = (x.to_numpy(dtype=float) for x in (o, h, lo, c))
    m = len(cv)
    le, lx, se, sx = (np.zeros(m, dtype=bool) for _ in range(4))
    dist = np.full(m, np.nan)
    pos, entry_i, s_ = 0, -1, np.nan
    for i in range(m):
        if pos != 0 and 0 <= entry_i <= i:               # the house stop from the fill price
            e = ov[entry_i]
            if (pos == 1 and lv[i] <= e * (1 - s_)) or (pos == -1 and hv[i] >= e * (1 + s_)):
                pos = 0
        if pos == 1 and entry_i <= i and x_long[i]:
            lx[i], pos = True, 0
            continue
        if pos == -1 and entry_i <= i and x_short[i]:
            sx[i], pos = True, 0
            continue
        if pos == 0 and i + 1 < m:
            if buy[i] and (cv[i] - ov[i]) / cv[i] > 0:
                d = (cv[i] - ov[i]) / cv[i]
                le[i], dist[i], pos, entry_i, s_ = True, d, 1, i + 1, d
            elif sell[i] and not buy[i] and (ov[i] - cv[i]) / cv[i] > 0:
                d = (ov[i] - cv[i]) / cv[i]
                se[i], dist[i], pos, entry_i, s_ = True, d, -1, i + 1, d
    return le, lx, se, sx, dist


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    le, lx, se, sx, _ = _run(bars_df, p)
    idx = bars_df.index
    return tuple(pd.Series(x, index=idx) for x in (le, lx, se, sx))


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    *_, dist = _run(bars_df, p)
    return {"sl_stop": pd.Series(dist, index=bars_df.index).shift(1)}


def portfolio_kwargs(**params):
    return {}
