"""WaveTrend oversold crosses with a 30-minute EMA pullback, broker days: a WaveTrend cross up under -53 with the close above the 30-minute EMA 200, a positive candle-MFI and a fresh cross back above the
30-minute EMA 50 after a run above it goes long (the mirror short); a 5 ATR(11) stop with a 6 ATR target (3 ATR for shorts); entries only from flat.
Port of FMZ strategy #442214 "Strategy of Indicators Combination Breakthrough Trend Tracking" (WT MFI RSI EMA PB STRAT).

FMZ source id: 442214

Source
    https://www.fmz.com/strategy/442214 (PineScript v4, FMZ last modified 2024-02-20 11:38:22).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 191-374), WT 12 / 12 (53 / -53); MFI area 80 x 200 - 2; EMA timeframe "30": EMA 200 / 50; ATR exits on (long 6 / 5, short 3 / 5, ATR 11); lowest-low exits off; dates from 2020; 100 % of equity, capital 5000
    long = close > ema200_30 and (wt1 and wt2 < 0) and cross(wt1, wt2) and wt2 <= -53 and wt2 - wt1 <= 0 and mfi > 0 and close crosses above ema50_30 and three closes above it 2-4, 5-7 or 8-10 bars back, no open trade -> entry long
    exits: stop = avg - 5 atr(11), limit = avg + 6 atr(11) at the fill bar (short: avg + 5 atr, avg - 3 atr), placed while a trade is open

Interpretation choices (Pine rules in SURVEY_README.md)
    * The 30-minute EMAs requested from a daily chart are the values at the last 30-minute bar inside
      the broker day (as #436765), built from the minutes in precompute. The ATR bracket is set from the
      fill bar's ATR in the script; the port uses the signal bar's: sl / tp = k ATR(11) / close, shifted one
      bar inside stops() and re-based on the fill (stated approximation, as #440797). The start date and
      the lowest-low exits (off) are not applied. Entries need no open trade: opposite entries cannot occur
      (entries only from flat). Stop module: portfolio_kwargs {} (driver D4). Stops on daily bars: mark
      coarse_bar_stop. The 100 % of equity size and capital are sizing. Daily bars are broker days (17:00
      America/New_York), stamped with their first minute. FREQ = "1D" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; bracket from signal-bar data (approximation stated).
    2 generic: PASS, WaveTrend, candle MFI and lower-timeframe EMA pullback with an ATR bracket.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: the percent-of-equity size and capital stored.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: broker day (17:00 America/New_York, DST by the zone); 30-minute EMAs from the day's last 30-minute bar.
Opposite entries cannot occur (entries only from flat).

Marks: coarse_bar_stop
"""
import numpy as np
import pandas as pd

NAME = "fmz_442214_wavetrend_mfi_ltf_ema_pullback_atr_bracket"
FAMILY = "multi_indicator_confluence"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "atr_stop": [5.0, 3.0],
    "atr_profit_long": [6.0, 4.0],
}
DEFAULT_PARAMS = {"atr_stop": 5.0, "atr_profit_long": 6.0, "atr_profit_short": 3.0, "atr_len": 11, "cl": 12,
                  "al": 12, "overbought": 53, "oversold": -53, "mfi_period": 80, "mfi_mult": 200.0,
                  "mfi_pos_y": 2.0, "len1": 200, "len2": 50}
LTF = "30min"  # the security() timeframe "30"


def broker_day(index):
    """Broker day of each timestamp: the session ending 17:00 America/New_York, labelled by its
    end date (as worker A's ports). The desktop binds this name to registry_schema.broker_day."""
    ny = index.tz_convert("America/New_York")
    return (ny + pd.Timedelta(hours=7)).normalize().tz_localize(None)


def precompute(raw_1m_df, symbol_key, **params):
    p = {**DEFAULT_PARAMS, **params}
    df = raw_1m_df[["open", "high", "low", "close"]].dropna(how="all")
    if df.index.tz is None:
        raise ValueError("raw_1m_df must have a tz-aware UTC index")
    lab = broker_day(df.index)
    bars = df.groupby(lab).agg({"open": "first", "high": "max", "low": "min", "close": "last"})
    first = pd.Series(df.index, index=df.index).groupby(lab).first()
    b30 = df["close"].resample(LTF, label="left", closed="left").last().dropna()
    day30 = broker_day(b30.index)
    for col, n in (("ema1_ltf", int(p["len1"])), ("ema2_ltf", int(p["len2"]))):
        e = b30.ewm(span=n, adjust=False).mean()
        bars[col] = e.groupby(day30).last().reindex(bars.index)   # the day's last 30-minute bar
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


def _setup(bars_df, p):
    o, h, lo, c = bars_df["open"], bars_df["high"], bars_df["low"], bars_df["close"]
    ap = (h + lo + c) / 3
    esa = ap.ewm(span=int(p["cl"]), adjust=False).mean()
    d = (ap - esa).abs().ewm(span=int(p["cl"]), adjust=False).mean()
    wt1 = ((ap - esa) / (0.015 * d)).ewm(span=int(p["al"]), adjust=False).mean()
    wt2 = wt1.rolling(4).mean()
    wx = ((wt1 > wt2) & (wt1.shift(1) <= wt2.shift(1))) | ((wt1 < wt2) & (wt1.shift(1) >= wt2.shift(1)))
    buy_s = wx & (wt2 <= float(p["oversold"])) & (wt2 - wt1 <= 0)
    sell_s = wx & (wt2 >= float(p["overbought"])) & (wt2 - wt1 >= 0)
    with np.errstate(divide="ignore", invalid="ignore"):
        body = ((c - o) / (h - lo).where(h != lo)) * float(p["mfi_mult"])
    mfi = body.rolling(int(p["mfi_period"])).mean() - float(p["mfi_pos_y"])
    e1, e2 = bars_df["ema1_ltf"], bars_df["ema2_ltf"]
    above = c > e2
    below = c < e2
    run_up = (above.shift(2, fill_value=False) & above.shift(3, fill_value=False) & above.shift(4, fill_value=False)) | (above.shift(5, fill_value=False) & above.shift(6, fill_value=False) & above.shift(7, fill_value=False)) \
        | (above.shift(8, fill_value=False) & above.shift(9, fill_value=False) & above.shift(10, fill_value=False))
    run_dn = (below.shift(2, fill_value=False) & below.shift(3, fill_value=False) & below.shift(4, fill_value=False)) | (below.shift(5, fill_value=False) & below.shift(6, fill_value=False) & below.shift(7, fill_value=False)) \
        | (below.shift(8, fill_value=False) & below.shift(9, fill_value=False) & below.shift(10, fill_value=False))
    wt1_on = wt1.notna() & (wt1 != 0)
    lc = (c > e1) & wt1_on & (wt2 < 0) & buy_s & (mfi > 0) & above & (c.shift(1) < e2.shift(1)) & run_up
    sc = (c < e1) & wt1_on & (wt2 > 0) & sell_s & (mfi < 0) & below & (c.shift(1) > e2.shift(1)) & run_dn
    pc = c.shift(1)
    tr = pd.concat([h - lo, (h - pc).abs(), (lo - pc).abs()], axis=1).max(axis=1)
    a = _rma(tr, int(p["atr_len"])) / c
    sl = float(p["atr_stop"]) * a
    tp = (float(p["atr_profit_long"]) * a).where(~sc, float(p["atr_profit_short"]) * a)
    return lc.to_numpy(), sc.to_numpy(), sl, tp


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    lc, sc, sl_s, tp_s = _setup(bars_df, p)
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
        if pos == 0 and i + 1 < m and not np.isnan(sl[i]):
            if lc[i]:
                le[i], pos, entry_i, s_, t_ = True, 1, i + 1, sl[i], tp[i]
            elif sc[i]:
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
