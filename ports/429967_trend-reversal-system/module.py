"""CCI pullback in an EMA + ATR-stop trend with a bracket, broker days: from flat, in an up-trend (EMA 21 above EMA 55 and
the 55-bar 5 ATR stop direction up), CCI 20 between -140 and -100 goes long with a stop at the ATR stop line and a
fixed target (mirror short).
Port of FMZ strategy #429967 "Trend Reversal System" (Oath).

FMZ source id: 429967

Source
    https://www.fmz.com/strategy/429967 (PineScript v4, FMZ last modified 2023-10-23 17:18:28).
    Verbatim copy: original_source.md. Read 2026-10-16 (FMZ-C).

Original signal (original_source.md lines 129-255), EMA 21 / 55, CCI 20 (level 1: -100 / -140, 100 / 140), ATR 55 x 5 with wicks, target 400 pips
    dir: ATR chandelier (hl2 -/+ 5 atr(55), ratcheted on low[1] / high[1]); uptrend = ema21 > ema55 and dir == 1
    buy1 = uptrend and -140 < cci <= -100 and no open trade -> entry long + exit(profit = 400, stop = longStop - spread)
    sell1 = downtrend and 100 <= cci < 140 and no open trade -> entry short + exit(profit = 400, stop = shortStop + spread)

Interpretation choices (Pine rules in SURVEY_README.md)
    * Only the level-1 bands are on by default (levels 2 and 3 are options). The 0.0002 spread is a price-unit
      constant of the author's FX setting: ignored (no costs in a module).
    * The stop is the signal bar's ATR stop line (as a fraction of its close, shifted one bar inside
      stops(), re-based on the fill). Criterion 2: the 400-pip target (40 USD at a 0.1 tick on daily BTC)
      becomes tp_atr x Wilder ATR(14) of the signal bar, about 0.04 ATR (judgement before any backtest).
    * Entries only from flat: "flat" follows the house bracket on bars. Opposite entries cannot occur.
      Stop module: portfolio_kwargs {} (driver D4). Stops on 1-day bars: mark coarse_bar_stop.
    * Daily bars are broker days (17:00 America/New_York), stamped with their first minute.
      FREQ = "1D" from the backtest header (period 1d).

Admission criteria
    1 fits the interface: PASS, bar-close orders; bracket fixed at entry.
    2 generic: ADAPT, the pip target -> an ATR multiple; the spread constant dropped.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: the capital-based order size stored; the bracket quoted in original_sizing.txt.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: ND429967 (2 members, best partner #439207, Jaccard 0.785); ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: broker day (17:00 America/New_York, DST by the zone); no venue-open rule.
Opposite entries cannot occur.

Marks: coarse_bar_stop
"""
import numpy as np
import pandas as pd

NAME = "fmz_429967_oath_cci_pullback_bracket"
FAMILY = "multi_indicator_confluence"  # proposed 2026-10-16 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "tp_atr": [0.04, 2.0],
    "mult": [5.0, 3.0],
}
DEFAULT_PARAMS = {"ema_short": 21, "ema_long": 55, "cci_len": 20, "ob1": 100, "ob2": 140, "os1": -100, "os2": -140,
                  "atr_len": 55, "mult": 5.0, "tp_atr": 0.04, "atr_tp_len": 14}


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


def _tr(bars_df):
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    pc = c.shift(1)
    return pd.concat([h - lo, (h - pc).abs(), (lo - pc).abs()], axis=1).max(axis=1, skipna=False)


def _setup(bars_df, p):
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    atr = (p["mult"] * _rma(_tr(bars_df), int(p["atr_len"]))).to_numpy()
    src = ((h + lo) / 2).to_numpy()
    hv, lv = h.to_numpy(dtype=float), lo.to_numpy(dtype=float)
    m = len(src)
    ls_, ss_ = np.full(m, np.nan), np.full(m, np.nan)
    d = np.ones(m, dtype=np.int8)
    for i in range(m):
        lraw, sraw = src[i] - atr[i], src[i] + atr[i]
        lp = ls_[i - 1] if i >= 1 and not np.isnan(ls_[i - 1]) else lraw
        sp = ss_[i - 1] if i >= 1 and not np.isnan(ss_[i - 1]) else sraw
        ls_[i] = max(lraw, lp) if i >= 1 and lv[i - 1] > lp else lraw
        ss_[i] = min(sraw, sp) if i >= 1 and hv[i - 1] < sp else sraw
        t = d[i - 1] if i >= 1 else 1
        if t == -1 and hv[i] > sp:
            t = 1
        elif t == 1 and lv[i] < lp:
            t = -1
        d[i] = t
    es = c.ewm(span=int(p["ema_short"]), adjust=False).mean()
    el = c.ewm(span=int(p["ema_long"]), adjust=False).mean()
    n = int(p["cci_len"])
    ma = c.rolling(n).mean()
    md = c.rolling(n).apply(lambda w: np.mean(np.abs(w - w.mean())), raw=True)
    cci = ((c - ma) / (0.015 * md.replace(0.0, np.nan))).to_numpy()
    up = ((es > el).to_numpy()) & (d == 1)
    dn = ((es < el).to_numpy()) & (d == -1)
    buy = up & (cci <= p["os1"]) & (cci > p["os2"])
    sell = dn & (cci >= p["ob1"]) & (cci < p["ob2"])
    cv = c.to_numpy(dtype=float)
    sl_l = (cv - ls_) / cv
    sl_s = (ss_ - cv) / cv
    tpf = (p["tp_atr"] * _rma(_tr(bars_df), int(p["atr_tp_len"])) / c).to_numpy()
    return buy, sell, sl_l, sl_s, tpf


def _run(bars_df, p):
    buy, sell, sl_l, sl_s, tpf = _setup(bars_df, p)
    ov, hv, lv = (bars_df[k].to_numpy(dtype=float) for k in ("open", "high", "low"))
    m = len(ov)
    le, se = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    sl_arr, tp_arr = np.full(m, np.nan), np.full(m, np.nan)
    pos, entry_i, s_, t_ = 0, -1, np.nan, np.nan
    for i in range(m):
        if pos != 0 and i >= entry_i:                    # house bracket from the fill price
            e = ov[entry_i]
            if pos == 1 and (lv[i] <= e * (1 - s_) or hv[i] >= e * (1 + t_)):
                pos = 0
            elif pos == -1 and (hv[i] >= e * (1 + s_) or lv[i] <= e * (1 - t_)):
                pos = 0
        if pos == 0 and buy[i] and sl_l[i] > 0:
            le[i], pos, entry_i, s_, t_ = True, 1, i + 1, sl_l[i], tpf[i]
            sl_arr[i], tp_arr[i] = s_, t_
        elif pos == 0 and sell[i] and sl_s[i] > 0:
            se[i], pos, entry_i, s_, t_ = True, -1, i + 1, sl_s[i], tpf[i]
            sl_arr[i], tp_arr[i] = s_, t_
    return le, se, sl_arr, tp_arr


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    le, se, _, _ = _run(bars_df, p)
    idx = bars_df.index
    false = pd.Series(False, index=idx)
    return pd.Series(le, index=idx), false, pd.Series(se, index=idx), false.copy()


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    _, _, sl_arr, tp_arr = _run(bars_df, p)
    idx = bars_df.index
    return {"sl_stop": pd.Series(sl_arr, index=idx).shift(1), "tp_stop": pd.Series(tp_arr, index=idx).shift(1)}


def portfolio_kwargs(**params):
    return {}
