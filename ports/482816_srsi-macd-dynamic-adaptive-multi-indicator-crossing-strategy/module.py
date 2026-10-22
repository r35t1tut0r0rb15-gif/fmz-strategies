"""Stochastic RSI 16 / 16 / 3 / 3 under 20 turning up (K above D or above a range-scaled MACD, K or MACD rising), broker days, long only from flat: a 2.5 ATR 14 stop and target around the fill, and Stochastic RSI over 80 turning down closes.
Port of FMZ strategy #482816 "动态自适应多指标交叉策略结合SRSI和MACD的智能风控系统-Dynamic-Adaptive-Multi-Indicator-Crossing-Strategy-with-SRSI-MACD-Smart-Risk-Control-System" (SRSI + MACD Strategy with Dynamic Stop-Loss and Take-Profit).

FMZ source id: 482816

Source
    https://www.fmz.com/strategy/482816 (PineScript v6, FMZ last modified 2025-02-27 17:44:09).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 96-158), RSI 16, Stochastic 16, K 3, D 3; MACD 12 / 26 / 9 scaled to K's 16-bar range; ATR 14 x 2.5; 10 % of equity
    buy = (diffTotal > 0 or k - d > 0) and (rising(k, 1) or rising(macd, 1)) and k < 20;  sell = (diffTotal <= 0 or k - d <= 0) and (falling(k, 1) or falling(macd, 1)) and k > 80
    buy and flat -> entry Buy;  position long -> exit(stop = avg - 2.5 atr, limit = avg + 2.5 atr), re-sent every bar;  sell -> close Buy

Interpretation choices (Pine rules in SURVEY_README.md)
    * diffTotal = ((k - d) + (k - normalisedMacd)) / 2, normalisedMacd = MACD's 16-bar min-max position
      scaled into K's 16-bar range, as written. The bracket is sent from the fill bar's close around the
      average price with that bar's ATR and re-sent every bar with the current ATR; the port fixes it
      from the fill at the signal bar's ATR (known at the fill open), active from the fill bar (as
      #440797), and marks the re-sent ATR distance trailing_stop_pending. The flat gate is followed in
      the signal loop with the bracket checked on each bar's high / low (as 449508). Long only. Stop
      module: portfolio_kwargs {} (driver D4). Stops on daily bars: mark coarse_bar_stop. The 10 % of
      equity size is sizing; the enable switches are on as defaulted. Daily bars are broker days
      (17:00 America/New_York), stamped with their first minute. FREQ = "1D" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; ATR bracket as fractions of the fill.
    2 generic: PASS, Stochastic RSI turns with a scaled MACD.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: 10 % of equity stored, not ported.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: broker day (17:00 America/New_York, DST by the zone); no venue-open rule.
Long only.

Marks: coarse_bar_stop, trailing_stop_pending
"""
import numpy as np
import pandas as pd

NAME = "fmz_482816_stochrsi16_macd_scaled_turn_atr2_5_bracket_long"
FAMILY = "stochastic_oscillator"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "risk_factor": [2.5, 1.5],
    "rsi_length": [16, 10],
}
DEFAULT_PARAMS = {"risk_factor": 2.5, "rsi_length": 16, "stoch_length": 16, "smooth_k": 3, "smooth_d": 3,
                  "atr_length": 14}


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
    up, dn = _rma(d.clip(lower=0), n), _rma((-d).clip(lower=0), n)
    r = 100 - 100 / (1 + up / dn)
    r = r.where(dn != 0, 100.0).where(up != 0, 0.0)
    return r.where(up.notna() & dn.notna())


def _atr(bars_df, n):
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    pc = c.shift(1)
    tr = pd.concat([h - lo, (h - pc).abs(), (lo - pc).abs()], axis=1).max(axis=1, skipna=False)
    tr.iloc[0] = h.iloc[0] - lo.iloc[0]
    return _rma(tr, n)


def _plan(bars_df, p):
    o, h, lo, c = bars_df["open"], bars_df["high"], bars_df["low"], bars_df["close"]

    def ema(x, n):
        return x.ewm(span=int(n), adjust=False).mean()

    n = int(p["rsi_length"])
    r = _rsi(c, n)
    sl_ = int(p["stoch_length"])
    rr = r.rolling(sl_).max() - r.rolling(sl_).min()
    k = (100 * (r - r.rolling(sl_).min()) / rr.where(rr > 0)).rolling(int(p["smooth_k"])).mean()
    d = k.rolling(int(p["smooth_d"])).mean()
    macd = ema(c, 12) - ema(c, 26)
    mr = macd.rolling(n).max() - macd.rolling(n).min()
    nm = (macd - macd.rolling(n).min()) / mr * (k.rolling(n).max() - k.rolling(n).min()) + k.rolling(n).min()
    dkd = k - d
    dtot = (dkd + (k - nm)) / 2
    buy = (((dtot > 0) | (dkd > 0)) & ((k > k.shift(1)) | (macd > macd.shift(1))) & (k < 20)).to_numpy()
    sell = (((dtot <= 0) | (dkd <= 0)) & ((k < k.shift(1)) | (macd < macd.shift(1))) & (k > 80)).to_numpy()
    dist = (float(p["risk_factor"]) * _atr(bars_df, int(p["atr_length"]))).to_numpy()
    ov, hv, lv = (x.to_numpy(dtype=float) for x in (o, h, lo))
    m = len(ov)
    le, lx = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    pos = False
    pend_in = pend_out = False
    sl = tp = np.nan
    for i in range(m):
        if pend_out:
            pos, pend_out = False, False
        if pend_in:
            pend_in = False
            if np.isnan(dist[i - 1]):
                pos = False                       # no level known: the entry is refused below
            else:
                pos = True
                sl, tp = ov[i] - dist[i - 1], ov[i] + dist[i - 1]
        if pos and (lv[i] <= sl or hv[i] >= tp):
            pos = False                           # the bracket closes it inside the bar
        if not pos and buy[i] and not np.isnan(dist[i]):
            le[i], pend_in = True, True
        elif pos and sell[i]:
            lx[i], pend_out = True, True
    idx = c.index
    return pd.Series(le, index=idx), pd.Series(lx, index=idx), pd.Series(dist, index=idx)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    le, lx, _ = _plan(bars_df, p)
    false = pd.Series(False, index=le.index)
    return le, lx, false, false.copy()


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    _, _, dist = _plan(bars_df, p)
    f = dist.shift(1) / bars_df["open"]
    f = f.where(f > 0)
    return {"sl_stop": f, "tp_stop": f.copy()}


def portfolio_kwargs(**params):
    return {}
