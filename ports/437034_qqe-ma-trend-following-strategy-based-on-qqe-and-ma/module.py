"""QQE channel-exit trades with a two-ribbon EMA direction filter, broker days: from flat, the first bar after the smoothed RSI first closes above 60, with the EMA 21 and its 4x-length twin both rising and the close
above the EMA 21 on that bar, goes long; the mirror (below 40, both falling) goes short; a long closes when a new run of QQE-cross-down / below-50 / below-40 bars starts, a short on the mirror.
Port of FMZ strategy #437034 "基于QQE和MA的趋势跟踪策略Trend-Following-Strategy-Based-on-QQE-and-MA" ([BT]QQEX v6.0).

FMZ source id: 437034

Source
    https://www.fmz.com/strategy/437034 (PineScript v3, FMZ last modified 2023-12-29 16:36:47).
    Verbatim copy: original_source.md. Read 2026-10-21 (FMZ-C).

Original signal (original_source.md lines 451-748), MA EMA 16 / 21 / 26, anchor x4; QQE RSI 14, smoothing 8, factor 5, threshold 10; trade signal XC, close signal XQ; MA filter off, direction filter on, first-only off; start 2018-06-12
    RSIndex = ema(rsi(close, 14), 8);  QQE bands RSIndex -+ 5 ema(ema(|dRSIndex|, 27), 27) with ratchets;  trend flips on cross(RSIndex, shortband[1]) / cross(longband[1], RSIndex)
    buy_ = QQEclong[1] == 1 and QQEflong[1];  sell_ mirror;  closeLong counts runs of (QQExshort == 1 or QQEzshort or QQEcshort);  tradestate 0 -> 1 / 2 on buy / sell == 1, back to 0 on closeLong / closeShort == 1

Interpretation choices (Pine rules in SURVEY_README.md)
    * With the defaults: trades on XC (threshold channel exit) signals, read one bar late as written (the
      buy uses QQEclong[1] == 1 and the filter of that bar); the filter is the mult = 4 branch: the medium
      EMA rising and the 84-bar EMA rising over 3 bars (rising() = above each of the last 3 values) and the
      close above the medium EMA. The XQ close fires on the FIRST bar of a run where the QQE line is above
      the index, or the index is under 50 or under 40 (counts used as booleans, as written); a run that
      started while flat cannot close a later trade until it ends. Entries only from flat (tradestate),
      so opposite entries cannot occur. The backtest start (2018) is a window: dropped. The MA types other
      than the default EMA are ported except VWMA (volume, check 8) and LAGMA (not offered). No sizing code.
      Daily bars are broker days (17:00 America/New_York), stamped with their first minute. FREQ = "1D" from
      the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, RSI-based QQE and average directions.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: DG437034 (2 members, best partner #439638, Jaccard 0.989); ND431270 (2 members, best partner #431270, Jaccard 0.733); ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: broker day (17:00 America/New_York, DST by the zone); no venue-open rule.
Opposite entries cannot occur.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_437034_qqe_channel_exit_ma_direction"
FAMILY = "rsi_oscillator"  # proposed 2026-10-21 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "rsi_len": [14, 21],
    "threshold": [10.0, 5.0],
}
DEFAULT_PARAMS = {"rsi_len": 14, "threshold": 10.0, "sf": 8, "qqe_factor": 5.0, "ma_type": "EMA", "len1": 16,
                  "len2": 21, "len3": 26, "anchor": 4}


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
    up = _rma(d.clip(lower=0), n)
    dn = _rma((-d).clip(lower=0), n)
    with np.errstate(divide="ignore", invalid="ignore"):
        r = 100.0 - 100.0 / (1.0 + up / dn)
    r = r.where(up != 0, 0.0).where(dn != 0, 100.0)    # Pine: down == 0 -> 100, else up == 0 -> 0
    return r.where(up.notna() & dn.notna())


def _ema(x, n):
    return x.ewm(span=n, adjust=False).mean()


def _wma(x, n):
    w = np.arange(1, n + 1, dtype=float)
    return x.rolling(n).apply(lambda v: np.dot(v, w) / w.sum(), raw=True)


def _smma(x, n):
    v, sma = x.to_numpy(dtype=float), x.rolling(n).mean().to_numpy()
    out = np.full(len(v), np.nan)
    for i in range(len(v)):
        prev = out[i - 1] if i else np.nan
        out[i] = sma[i] if np.isnan(prev) else (prev * (n - 1) + v[i]) / n
    return pd.Series(out, index=x.index)


def _ssma(x, n):
    a1 = np.exp(-1.414 * 3.14159 / n)
    b1 = 2 * a1 * np.cos(1.414 * 3.14159 / n)
    c2, c3 = b1, -a1 * a1
    c1 = 1 - c2 - c3
    v = x.to_numpy(dtype=float)
    out = np.full(len(v), np.nan)
    for i in range(len(v)):
        s1 = v[i - 1] if i and not np.isnan(v[i - 1]) else 0.0
        o1 = out[i - 1] if i and not np.isnan(out[i - 1]) else 0.0
        o2 = out[i - 2] if i > 1 and not np.isnan(out[i - 2]) else 0.0
        out[i] = c1 * (v[i] + s1) / 2 + c2 * o1 + c3 * o2
    return pd.Series(out, index=x.index)


def _variant(kind, x, n):
    if kind == "EMA":
        return _ema(x, n)
    if kind == "WMA":
        return _wma(x, n)
    if kind == "SMMA":
        return _smma(x, n)
    if kind == "DEMA":
        e = _ema(x, n)
        return 2 * e - _ema(e, n)
    if kind == "TEMA":
        e = _ema(x, n)
        return 3 * (e - _ema(e, n)) + _ema(_ema(e, n), n)
    if kind == "HullMA":
        return _wma(2 * _wma(x, n // 2) - _wma(x, n), int(round(np.sqrt(n))))
    if kind == "SSMA":
        return _ssma(x, n)
    if kind == "ZEMA":
        e = _ema(x, n)
        return e + (e - _ema(e, n))
    if kind == "TMA":
        return x.rolling(n).mean().rolling(n).mean()
    if kind == "VWMA":
        raise ValueError("MA type 'VWMA' not ported (volume, check 8)")
    return x.rolling(n).mean()


def _rising(x, n):
    prev = pd.concat([x.shift(k) for k in range(1, n + 1)], axis=1).max(axis=1, skipna=False)
    return x > prev


def _falling(x, n):
    prev = pd.concat([x.shift(k) for k in range(1, n + 1)], axis=1).min(axis=1, skipna=False)
    return x < prev


def _runs(cond):
    out = np.zeros(len(cond), dtype=int)
    k = 0
    for i, v in enumerate(cond):
        k = k + 1 if v else 0
        out[i] = k
    return out


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    c = bars_df["close"]
    rl = int(p["rsi_len"])
    wp = rl * 2 - 1
    rsx = _ema(_rsi(c, rl), int(p["sf"]))
    atr_rsi = (rsx.shift(1) - rsx).abs()
    delta = _ema(_ema(atr_rsi, wp), wp) * float(p["qqe_factor"])
    ri, nsb, nlb = rsx.to_numpy(), (rsx + delta).to_numpy(), (rsx - delta).to_numpy()
    m = len(ri)
    lb, sb, tl = np.full(m, np.nan), np.full(m, np.nan), np.full(m, np.nan)
    trend = 1
    with np.errstate(invalid="ignore"):
        for i in range(m):
            r1 = ri[i - 1] if i else np.nan
            lb1 = lb[i - 1] if i else 0.0
            sb1 = sb[i - 1] if i else 0.0
            lb[i] = (np.nan if np.isnan(nlb[i]) or np.isnan(lb1) else max(lb1, nlb[i])) \
                if (r1 > lb1 and ri[i] > lb1) else nlb[i]
            sb[i] = (np.nan if np.isnan(nsb[i]) or np.isnan(sb1) else min(sb1, nsb[i])) \
                if (r1 < sb1 and ri[i] < sb1) else nsb[i]
            sb2 = sb[i - 2] if i > 1 else np.nan
            lb2 = lb[i - 2] if i > 1 else np.nan
            x_up = (ri[i] > sb1 and r1 <= sb2) or (ri[i] < sb1 and r1 >= sb2)
            x_dn = (lb1 > ri[i] and lb2 <= r1) or (lb1 < ri[i] and lb2 >= r1)
            if x_up:
                trend = 1
            elif x_dn:
                trend = -1
            tl[i] = lb[i] if trend == 1 else sb[i]
        xl = _runs(tl < ri)
        xs = _runs(tl > ri)
    th = float(p["threshold"])
    zl, zs = _runs((rsx >= 50).to_numpy()), _runs((rsx < 50).to_numpy())
    cl, cs = _runs((rsx > 50 + th).to_numpy()), _runs((rsx < 50 - th).to_numpy())
    mult = int(p["anchor"]) if int(p["anchor"]) > 0 else 1
    kind = p["ma_type"]
    ma_med = _variant(kind, c, int(p["len2"]))
    ma_med_alt = _variant(kind, c, int(p["len2"]) * mult)
    if mult == 1:
        fl = _rising(ma_med, 3)
        fs = _falling(ma_med, 3)
    else:
        fl = _rising(ma_med, 3) & _rising(ma_med_alt, 3) & (c > ma_med)
        fs = _falling(ma_med, 3) & _falling(ma_med_alt, 3) & (c < ma_med)
    fl1, fs1 = fl.shift(1, fill_value=False).to_numpy(), fs.shift(1, fill_value=False).to_numpy()
    cl1 = np.concatenate(([0], cl[:-1]))
    cs1 = np.concatenate(([0], cs[:-1]))
    buy = _runs((cl1 == 1) & fl1)
    sell = _runs((cs1 == 1) & fs1)
    close_l = _runs((xs == 1) | (zs > 0) | (cs > 0))
    close_s = _runs((xl == 1) | (zl > 0) | (cl == 1))
    le, lx = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    se, sx = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    state = 0
    for i in range(m):
        if state == 0:
            new = 1 if buy[i] == 1 else (2 if sell[i] == 1 else 0)
        elif (state == 1 and close_l[i] == 1) or (state == 2 and close_s[i] == 1):
            new = 0
        else:
            new = state
        if new != state:
            if new == 1:
                le[i] = True
            elif new == 2:
                se[i] = True
            elif state == 1:
                lx[i] = True
            else:
                sx[i] = True
        state = new
    ix = bars_df.index
    return pd.Series(le, index=ix), pd.Series(lx, index=ix), pd.Series(se, index=ix), pd.Series(sx, index=ix)


def portfolio_kwargs(**params):
    return {}
