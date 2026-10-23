"""Two long setups sharing one position, broker days: a mean-reversion entry (the 8-bar rolling VWAP crossing under 98 % of the 10-bar one, EMA 5 of RSI 2 under 30, the close under the 50-bar VWAP) that closes when the close rises above the 50-bar VWAP; and a trend entry (rising VWAP Ichimoku lead lines, positive rising TSV, a close above the Bollinger band of the lead lines and above VIDYA 20) that closes when both lead lines fall; long only.
Port of FMZ strategy #430578 "Dual Moving Average Crossover Algorithmic Trading Strategy" (HYE Combo Market [Strategy] (Vwap Mean Reversion + Trend Hunter)).

FMZ source id: 430578

Source
    https://www.fmz.com/strategy/430578 (PineScript v4, FMZ last modified 2023-10-30 15:27:34).
    Verbatim copy: original_source.md. Read 2026-10-23 (FMZ-C).

Original signal (original_source.md lines 240-409), VWAP 8 / 10 / 50, 2 % below, RSI 2 EMA 5 < 30; lead lines 9 / 13 (slow) and 3 / 7 (fast); BB 20 / 2; TSV 20 / EMA 7; VIDYA 20 of hl2
    crossunder(vwap8, 0.98 x vwap10) and ema(rsi(close, 2), 5) < 30 and close < vwap50 and flat -> entry BUY-M;  close > vwap50 -> close BUY-M
    fast and slow lead lines rising and tsv > 0 and tsv > ema(tsv, 7) and close > upper and close > vidya and flat -> entry BUY-T;  both lead lines falling -> close BUY-T

Interpretation choices (Pine rules in SURVEY_README.md)
    * Each entry needs a flat position, so only one setup holds the position at a time and only its own
      close rule ends it; when both fire on one bar the mean-reversion entry (sent first) fills and the
      second one is refused by pyramiding 1. VIDYA starts from nz = 0, as written; the fast Kijun line
      reuses the slow typical price (the same hlc3). The 2000 .. 2021 inputs are not used (inDateRange is
      true). Long only. The 100 % of equity size and commission are sizing / costs. Daily bars are broker
      days (17:00 America/New_York), stamped with their first minute. FREQ = "1D" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, VWAP mean reversion combined with a VWAP lead-line trend setup.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: 100 % of equity, capital 1000, commission 0.025 stored, not ported.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: used: the bars' volume column (broker tick volume of the cTrader M1 data, summed per bar) in the rolling VWAPs, the lead lines and the TSV; exchange volume to be compared later (Austin, 2026-10-23).
Session open: broker day (17:00 America/New_York, DST by the zone); no venue-open rule.
Long only. Opposite entries cannot occur.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_430578_vwap_mean_reversion_plus_vwap_lead_line_trend_long"
FAMILY = "volume_weighted_ma"  # proposed 2026-10-23 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "percent_below": [2.0, 1.0],
    "rsi_level": [30.0, 20.0],
}
DEFAULT_PARAMS = {"percent_below": 2.0, "rsi_level": 30.0, "small": 8, "big": 10, "mean": 50, "rsi_period": 2,
                  "rsi_ema": 5, "slow_t": 9, "slow_k": 13, "fast_t": 3, "fast_k": 7, "bb_length": 20, "bb_mult": 2.0,
                  "tsv_length": 20, "tsv_ema": 7, "vidya_len": 20}


def broker_day(index):
    """Broker day of each timestamp: the session ending 17:00 America/New_York, labelled by its
    end date (as worker A's ports). The desktop binds this name to registry_schema.broker_day."""
    ny = index.tz_convert("America/New_York")
    return (ny + pd.Timedelta(hours=7)).normalize().tz_localize(None)


def precompute(raw_1m_df, symbol_key, **params):
    df = raw_1m_df[["open", "high", "low", "close", "volume"]].dropna(subset=["close"])
    if df.index.tz is None:
        raise ValueError("raw_1m_df must have a tz-aware UTC index")
    lab = broker_day(df.index)
    bars = df.groupby(lab).agg({"open": "first", "high": "max", "low": "min", "close": "last", "volume": "sum"})
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


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    h, lo, c, v = (bars_df[k] for k in ("high", "low", "close", "volume"))
    tpv = (h + lo + c) / 3 * v
    vw = lambda n: tpv.rolling(n).sum() / v.rolling(n).sum()
    small, big, mean = vw(int(p["small"])), vw(int(p["big"])), vw(int(p["mean"]))
    d = c.diff()
    n = int(p["rsi_period"])
    rsi = 100 - 100 / (1 + _rma(d.clip(lower=0), n) / _rma((-d).clip(lower=0), n))
    rsie = rsi.ewm(span=int(p["rsi_ema"]), adjust=False).mean()
    buy_ma = (100 - float(p["percent_below"])) / 100 * big
    ent_m = ((small < buy_ma) & (small.shift(1) >= buy_ma.shift(1)) & (rsie < float(p["rsi_level"])) & (c < mean)).to_numpy()
    ex_m = (c > mean).to_numpy()
    mid = lambda x, k: (x.rolling(k).min() + x.rolling(k).max()) / 2
    st, sk, ft, fk = (int(p[k]) for k in ("slow_t", "slow_k", "fast_t", "fast_k"))
    slow = (mid(vw(st), st) + mid(vw(sk), sk)) / 2
    fast = (mid(vw(ft), ft) + mid(vw(fk), fk)) / 2
    bbl = (fast + slow) / 2
    bn = int(p["bb_length"])
    upper = bbl.rolling(bn).mean() + float(p["bb_mult"]) * bbl.rolling(bn).std(ddof=0)
    tsv = (v * d).fillna(0.0).rolling(int(p["tsv_length"])).sum()
    tsve = tsv.ewm(span=int(p["tsv_ema"]), adjust=False).mean()
    src = (h + lo) / 2
    mom = src.diff()
    vl = int(p["vidya_len"])
    up_s, dn_s = mom.clip(lower=0).rolling(vl).sum(), (-mom).clip(lower=0).rolling(vl).sum()
    k = (2 / (vl + 1)) * ((up_s - dn_s) / (up_s + dn_s)).abs()
    kv, sv = k.to_numpy(), src.to_numpy(dtype=float)
    vid = np.full(len(sv), np.nan)
    prev = 0.0
    for i in range(len(sv)):
        vid[i] = sv[i] * kv[i] + prev * (1 - kv[i])
        prev = 0.0 if np.isnan(vid[i]) else vid[i]
    ent_t = ((fast > fast.shift(1)) & (slow > slow.shift(1)) & (tsv > 0) & (tsv > tsve) & (c > upper)
             & (c > pd.Series(vid, index=c.index))).to_numpy()
    ex_t = ((fast < fast.shift(1)) & (slow < slow.shift(1))).to_numpy()
    m = len(ent_m)
    le, lx = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    held = None                                          # "M", "T" or None
    for i in range(m):
        if held == "M" and ex_m[i]:
            lx[i], held = True, None
        elif held == "T" and ex_t[i]:
            lx[i], held = True, None
        elif held is None and i + 1 < m:
            if ent_m[i]:
                le[i], held = True, "M"
            elif ent_t[i]:
                le[i], held = True, "T"
    ix = bars_df.index
    false = pd.Series(False, index=ix)
    return pd.Series(le, index=ix), pd.Series(lx, index=ix), false, false.copy()


def portfolio_kwargs(**params):
    return {}
