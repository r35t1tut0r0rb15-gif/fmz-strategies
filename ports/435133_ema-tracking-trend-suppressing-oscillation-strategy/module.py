"""EMA 200, Trend Trader and Schaff Trend Cycle agreement, broker days, from flat: when all three turn up together (close
above the EMA 200 and the trend line, the STC rising) a long is opened with a stop under the lower of 0.1 % below the close
and the two previous lows and a 1 R target; the down mirror opens a short.
Port of FMZ strategy #435133 "EMA Tracking Trend Suppressing Oscillation Strategy" (EMA + TTS + STC).

FMZ source id: 435133

Source
    https://www.fmz.com/strategy/435133 (PineScript v5, FMZ last modified 2023-12-12 15:52:37).
    Verbatim copy: original_source.md. Read 2026-10-17 (FMZ-C).

Original signal (original_source.md lines 160-244), EMA 200; Trend Trader 21 x 3; STC 12 / 26 / 50, factor 0.5; profit 0.1 %
    pos = all three up ? 1 : all three down ? -1 : 0;  pos changes to 1 and flat -> entry long, exit(stop = min(close (1 - 0.1 %), low[1] x 0.9998, low[2] x 0.9998), limit = close + (close - stop))
    shorts mirror (stop = max(close (1 + 0.1 %), high[1] x 1.0002, high[2] x 1.0002))

Interpretation choices (Pine rules in SURVEY_README.md)
    * The Trend Trader line ret starts from the close (nz(ret[1], close)); its side is the close
      against it. The STC is the double-stochastic of the MACD 26 / 50 over 12 bars with factor
      0.5, as written; its side is its slope.
    * The bracket comes from the signal bar, as fractions of the signal close shifted one bar
      inside stops() (re-based on the fill). Entries only from flat: "flat" follows the house bracket
      on bars. Opposite entries cannot occur. Stop module: portfolio_kwargs {} (driver D4). Stops on
      daily bars: mark coarse_bar_stop. Daily bars are broker days (17:00 America/New_York),
      stamped with their first minute. FREQ = "1D" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; bracket from the signal bar.
    2 generic: PASS, average, trend-line and cycle states with swing exits.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: the strategy() 100 % of equity and commission stored.
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

NAME = "fmz_435133_ema_tts_stc_bracket"
FAMILY = "multi_indicator_confluence"  # proposed 2026-10-17 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "tt_mult": [3.0, 2.0],
    "profit": [0.001, 0.01],
}
DEFAULT_PARAMS = {"tt_len": 21, "tt_mult": 3.0, "stc_len": 12, "stc_fast": 26, "stc_slow": 50, "factor": 0.5,
                  "profit": 0.001}


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


def _wma(x, n):
    w = np.arange(1, n + 1, dtype=float)
    return x.rolling(n).apply(lambda a: np.dot(a, w) / w.sum(), raw=True)


def _stc(c, n, fast, slow, f):
    mac = (c.ewm(span=fast, adjust=False).mean() - c.ewm(span=slow, adjust=False).mean()).to_numpy()
    s = pd.Series(mac)
    lo1, rg1 = s.rolling(n).min().to_numpy(), (s.rolling(n).max() - s.rolling(n).min()).to_numpy()
    m = len(mac)
    cc, dd = np.zeros(m), np.zeros(m)
    prev_c = 0.0
    for i in range(m):
        prev_c = (mac[i] - lo1[i]) / rg1[i] * 100 if rg1[i] > 0 else prev_c
        cc[i] = prev_c
        dd[i] = cc[i] if i == 0 else dd[i - 1] + f * (cc[i] - dd[i - 1])
    d = pd.Series(dd)
    lo2, rg2 = d.rolling(n).min().to_numpy(), (d.rolling(n).max() - d.rolling(n).min()).to_numpy()
    ee = np.zeros(m)
    prev_d, prev_e = 0.0, np.nan
    for i in range(m):
        prev_d = (dd[i] - lo2[i]) / rg2[i] * 100 if rg2[i] > 0 else prev_d
        prev_e = prev_d if np.isnan(prev_e) else prev_e + f * (prev_d - prev_e)
        ee[i] = prev_e
    return ee


def _run(bars_df, p):
    o, h, lo, c = (bars_df[k] for k in ("open", "high", "low", "close"))
    cv = c.to_numpy(dtype=float)
    ema = c.ewm(span=200, adjust=False).mean().to_numpy()
    n = int(p["tt_len"])
    c1 = c.shift(1)
    tr = pd.concat([h - lo, (h - c1).abs(), (lo - c1).abs()], axis=1).max(axis=1)
    tr.iloc[0] = np.nan
    avg_tr = _wma(tr, n)
    hi_l = (h.rolling(n).max().shift(1) - avg_tr.shift(1) * float(p["tt_mult"])).to_numpy()
    lo_l = (lo.rolling(n).min().shift(1) + avg_tr.shift(1) * float(p["tt_mult"])).to_numpy()
    stc = _stc(c, int(p["stc_len"]), int(p["stc_fast"]), int(p["stc_slow"]), float(p["factor"]))
    m = len(cv)
    pos_v = np.zeros(m, dtype=np.int8)
    ret, pt = np.nan, 0
    with np.errstate(invalid="ignore"):
        for i in range(m):
            if cv[i] > hi_l[i] and cv[i] > lo_l[i]:
                ret = hi_l[i]
            elif cv[i] < lo_l[i] and cv[i] < hi_l[i]:
                ret = lo_l[i]
            elif np.isnan(ret):
                ret = cv[i]
            pt = 1 if cv[i] > ret else (-1 if cv[i] < ret else pt)
            pe = -1 if cv[i] < ema[i] else 1
            ps = 1 if (i > 0 and stc[i] > stc[i - 1]) else -1
            pos_v[i] = 1 if (pe == 1 and pt == 1 and ps == 1) else (-1 if (pe == -1 and pt == -1 and ps == -1) else 0)
    pr = float(p["profit"])
    hv, lv, ov = h.to_numpy(dtype=float), lo.to_numpy(dtype=float), o.to_numpy(dtype=float)
    l1, l2 = lo.shift(1).to_numpy(), lo.shift(2).to_numpy()
    h1, h2 = h.shift(1).to_numpy(), h.shift(2).to_numpy()
    le, se = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    sl = np.full(m, np.nan)
    pos, ei, s_ = 0, -1, np.nan
    for i in range(m):
        if pos != 0 and i >= ei:                          # the house bracket (1 R) from the fill price
            e0 = ov[ei]
            if pos == 1 and (lv[i] <= e0 * (1 - s_) or hv[i] >= e0 * (1 + s_)):
                pos = 0
            elif pos == -1 and (hv[i] >= e0 * (1 + s_) or lv[i] <= e0 * (1 - s_)):
                pos = 0
        chg = i > 0 and pos_v[i] != pos_v[i - 1]
        if pos == 0 and chg and pos_v[i] == 1:
            stop = np.nanmin([cv[i] * (1 - pr), l1[i] * 0.9998, l2[i] * 0.9998])
            f = (cv[i] - stop) / cv[i]
            if f > 0:
                le[i], pos, ei, s_ = True, 1, i + 1, f
                sl[i] = f
        elif pos == 0 and chg and pos_v[i] == -1:
            stop = np.nanmax([cv[i] * (1 + pr), h1[i] * 1.0002, h2[i] * 1.0002])
            f = (stop - cv[i]) / cv[i]
            if f > 0:
                se[i], pos, ei, s_ = True, -1, i + 1, f
                sl[i] = f
    return le, se, sl


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    le, se, _ = _run(bars_df, p)
    ix = bars_df.index
    false = pd.Series(False, index=ix)
    return pd.Series(le, index=ix), false, pd.Series(se, index=ix), false.copy()


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    _, _, sl = _run(bars_df, p)
    s = pd.Series(sl, index=bars_df.index).shift(1)
    return {"sl_stop": s, "tp_stop": s.copy()}


def portfolio_kwargs(**params):
    return {}
