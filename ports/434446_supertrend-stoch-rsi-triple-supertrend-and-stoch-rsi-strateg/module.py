"""Three Supertrends, a stochastic RSI cross and an EMA 200, broker days: with the close above the EMA, two neighbouring
Supertrends (fast + medium or medium + slow) up for two bars and the stochastic-RSI K crossing above D, go long with a
stop 2.7 ATR 14 under the close and a target 1.6 ATR 14 above it; the mirror goes short. A new trade waits until the
script's own tracker has seen the previous one's level touched.
Port of FMZ strategy #434446 "三重SuperTrend和Stoch-RSI策略Triple-SuperTrend-and-Stoch-RSI-Strategy" (3x Supertrend and Stoch RSI).

FMZ source id: 434446

Source
    https://www.fmz.com/strategy/434446 (PineScript v4, FMZ last modified 2023-12-06 14:29:00).
    Verbatim copy: original_source.md. Read 2026-10-17 (FMZ-C).

Original signal (original_source.md lines 188-301), Supertrends 1 / 10, 2 / 11, 3 / 12; stoch RSI 3 / 3 / 14 / 14, restriction off; EMA 200; SL 2.7 ATR 14, TP 1.6 ATR 14
    up_n = dir_n == -1 and dir_n[1] == -1 (down_n mirror);  long = close > ema200 and ((up1 and up2) or (up2 and up3)) and crossover(k, d) and not long and not drawing
    long -> long, drawing := true, TP = close + 1.6 atr, SL = close - 2.7 atr, entry long, exit(limit = TP, stop = SL);  shorts mirror
    long and (high[1] >= TP or low[1] <= SL) -> drawing := false, long := false;  shorts mirror

Interpretation choices (Pine rules in SURVEY_README.md)
    * The tracker (long / short / drawing, the levels from the signal close, tested on the previous
      bar's high / low, also on the signal bar itself) is the script's own state and is ported as a
      loop: it gates the entries. The broker bracket is ported as fractions of the signal close
      (2.7 / 1.6 ATR over the close), shifted one bar inside stops() (re-based on the fill).
    * Pine's built-in supertrend (dir -1 = up). The fixed quantity 10 is sizing. A new entry while the
      house position is still open (the tracker's levels differ slightly from the fill-based ones)
      reverses or is ignored: REVERSAL INTENDED. Stop module: portfolio_kwargs {} (driver D4). Stops
      on daily bars: mark coarse_bar_stop. Daily bars are broker days (17:00 America/New_York),
      stamped with their first minute. FREQ = "1D" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; bracket from the signal bar.
    2 generic: PASS, Supertrends, a stochastic RSI and ATR exits.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: the fixed quantity 10 stored.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: broker day (17:00 America/New_York, DST by the zone); no venue-open rule.
REVERSAL INTENDED.

Marks: coarse_bar_stop
"""
import numpy as np
import pandas as pd

NAME = "fmz_434446_triple_supertrend_stoch_rsi"
FAMILY = "supertrend"  # proposed 2026-10-17 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "ema_len": [200, 100],
    "tp_mult": [1.6, 3.0],
}
DEFAULT_PARAMS = {"st1_len": 10, "st1_mult": 1.0, "st2_len": 11, "st2_mult": 2.0, "st3_len": 12, "st3_mult": 3.0,
                  "k_s": 3, "d_s": 3, "rsi_len": 14, "stoch_len": 14, "ema_len": 200, "sl_len": 14, "sl_mult": 2.7,
                  "tp_len": 14, "tp_mult": 1.6}


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


def _atr(h, lo, c, n):
    c1 = c.shift(1)
    tr = pd.concat([h - lo, (h - c1).abs(), (lo - c1).abs()], axis=1).max(axis=1)
    tr.iloc[0] = np.nan
    return tr.ewm(alpha=1 / n, adjust=False).mean().to_numpy()


def _st_dir(h, lo, c, factor, n):
    """Direction of Pine's built-in supertrend(factor, atrPeriod): -1 up, 1 down."""
    atr = _atr(h, lo, c, n)
    hl2 = ((h + lo) / 2).to_numpy(dtype=float)
    cv = c.to_numpy(dtype=float)
    m = len(cv)
    lb, ub, st = np.full(m, np.nan), np.full(m, np.nan), np.full(m, np.nan)
    dr = np.ones(m)
    for i in range(m):
        lo_b, up_b = hl2[i] - factor * atr[i], hl2[i] + factor * atr[i]
        pl = lb[i - 1] if i > 0 and not np.isnan(lb[i - 1]) else 0.0
        pu = ub[i - 1] if i > 0 and not np.isnan(ub[i - 1]) else 0.0
        cp = cv[i - 1] if i > 0 else np.nan
        lb[i] = lo_b if (lo_b > pl or cp < pl) else pl
        ub[i] = up_b if (up_b < pu or cp > pu) else pu
        if np.isnan(atr[i]):
            lb[i], ub[i] = np.nan, np.nan
        if i == 0 or np.isnan(atr[i - 1]):
            dr[i] = 1
        elif st[i - 1] == ub[i - 1]:
            dr[i] = -1 if cv[i] > ub[i] else 1
        else:
            dr[i] = 1 if cv[i] < lb[i] else -1
        st[i] = lb[i] if dr[i] == -1 else ub[i]
    return dr


def _run(bars_df, p):
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    ups, dns = [], []
    for j in (1, 2, 3):
        dr = _st_dir(h, lo, c, float(p[f"st{j}_mult"]), int(p[f"st{j}_len"]))
        d1 = np.concatenate(([np.nan], dr[:-1]))
        ups.append((dr == -1) & (d1 == -1))
        dns.append((dr == 1) & (d1 == 1))
    ch = c.diff()
    n = int(p["rsi_len"])
    g = ch.clip(lower=0).ewm(alpha=1 / n, adjust=False).mean()
    ls = (-ch.clip(upper=0)).ewm(alpha=1 / n, adjust=False).mean()
    rsi = (100 - 100 / (1 + g / ls)).where(ls != 0, 100.0).where(g.notna())
    sn = int(p["stoch_len"])
    rl, rh = rsi.rolling(sn).min(), rsi.rolling(sn).max()
    k = (100 * (rsi - rl) / (rh - rl)).rolling(int(p["k_s"])).mean()
    d = k.rolling(int(p["d_s"])).mean()
    xu = ((k > d) & (k.shift(1) <= d.shift(1))).to_numpy()
    xd = ((k < d) & (k.shift(1) >= d.shift(1))).to_numpy()
    ema = c.ewm(span=int(p["ema_len"]), adjust=False).mean().to_numpy()
    stop_sz = _atr(h, lo, c, int(p["sl_len"])) * float(p["sl_mult"])
    prof_sz = _atr(h, lo, c, int(p["tp_len"])) * float(p["tp_mult"])
    cv, hv, lv = c.to_numpy(dtype=float), h.to_numpy(dtype=float), lo.to_numpy(dtype=float)
    base_l = (cv > ema) & ((ups[0] & ups[1]) | (ups[1] & ups[2])) & xu
    base_s = (cv < ema) & ((dns[0] & dns[1]) | (dns[1] & dns[2])) & xd
    m = len(cv)
    le, se = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    sl, tp = np.full(m, np.nan), np.full(m, np.nan)
    lg = sh = dw = False
    TP = SL = 0.0
    for i in range(m):
        lc = base_l[i] and not lg and not dw
        sc = base_s[i] and not sh and not dw
        if lc:
            lg, sh, dw = True, False, True
            TP, SL = cv[i] + prof_sz[i], cv[i] - stop_sz[i]
            le[i], sl[i], tp[i] = True, stop_sz[i] / cv[i], prof_sz[i] / cv[i]
        if sc:
            sh, lg, dw = True, False, True
            TP, SL = cv[i] - prof_sz[i], cv[i] + stop_sz[i]
            se[i], sl[i], tp[i] = True, stop_sz[i] / cv[i], prof_sz[i] / cv[i]
        if i > 0 and lg and (hv[i - 1] >= TP or lv[i - 1] <= SL):
            dw, lg = False, False
        if i > 0 and sh and (lv[i - 1] <= TP or hv[i - 1] >= SL):
            dw, sh = False, False
    return le, se, sl, tp


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    le, se, _, _ = _run(bars_df, p)
    ix = bars_df.index
    false = pd.Series(False, index=ix)
    return pd.Series(le, index=ix), false, pd.Series(se, index=ix), false.copy()


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    _, _, sl, tp = _run(bars_df, p)
    ix = bars_df.index
    return {"sl_stop": pd.Series(sl, index=ix).shift(1), "tp_stop": pd.Series(tp, index=ix).shift(1)}


def portfolio_kwargs(**params):
    return {}
