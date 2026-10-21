"""Three volatility stops with an ATR "Renko" step from 4-hour values, broker days, long only: with the close above three stacked volatility stops (5, 10 and 15 ATR 26 of ohlc4, the tightest highest) on a bar
whose close steps the Renko box up, go long; a close crossing under the tightest stop or a Renko step down closes it.
Port of FMZ strategy #436765 "融合多重止损的趋势追踪型Intraday策略Intraday-Trend-Following-Strategy-with-Multiple-Stop-Loss" (Lancelot vstop intraday strategy).

FMZ source id: 436765

Source
    https://www.fmz.com/strategy/436765 (PineScript v4, FMZ last modified 2023-12-27 15:30:07).
    Verbatim copy: original_source.md. Read 2026-10-21 (FMZ-C).

Original signal (original_source.md lines 115-329), Vstop 26 x 3 (multipliers 5 / 10 / 15), Renko time frame 240, ATR 60
    vstopX = volatility stop of ohlc4 with atr(26) x 5 / 10 / 15;  long cond = close above all three and vstopa > vstopb > vstopc;  HIGH / LOW / ATR = security(tickerid, "240", high / low / atr(60))
    RENKOUP / RENKODN seeded at (HIGH + LOW) / 2 +- ATR / 2;  UP when close >= RENKOUP[1] + 3 / 2 / 1 H (box moves 3 / 2 / 1 ATR), DN mirror;  entry Long when long cond and UP;  close Long when crossunder(close, vstopa) or DN

Interpretation choices (Pine rules in SURVEY_README.md)
    * The 4-hour values requested from a daily chart are the day's LAST 4-hour bar (a lower time frame
      returns its last bar inside the chart bar). The 4-hour bars are counted from the broker day's start
      (17:00 America/New_York), six per day, so the last one ends with the day; ATR(60) runs on that 4-hour
      series. The volatility stops follow the script's nz() seeds (the first minimum is 0) as written.
      The Renko box follows the script: the step tests the previous box, the moves use the current ATR,
      only the first true test of the six applies. The three Vstop lengths (all 26) are swept together.
      The short side is commented out in the source: long only. Same-bar entry and close: the close only
      applies to an open position. Long only. The 100 % of equity size is sizing. Daily bars are broker
      days, stamped with their first minute. FREQ = "1D" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; the 4-hour values end with the daily bar.
    2 generic: PASS, volatility stops and ATR steps.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: the percent-of-equity size and commission stored.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: broker day (17:00 America/New_York, DST by the zone), 4-hour bars counted from its start; no venue-open rule.
Long only.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_436765_triple_vstop_renko_step_long"
FAMILY = "atr_trailing_line"  # proposed 2026-10-21 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "vlen": [26, 40],
    "renko_atr": [60, 30],
}
DEFAULT_PARAMS = {"vlen": 26, "renko_atr": 60, "mult_a": 5.0, "mult_b": 10.0, "mult_c": 15.0, "tf_minutes": 240}


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


def _tr(h, lo, c):
    pc = c.shift(1)
    return pd.concat([h - lo, (h - pc).abs(), (lo - pc).abs()], axis=1).max(axis=1)


def precompute(raw_1m_df, symbol_key, **params):
    p = {**DEFAULT_PARAMS, **params}
    df = raw_1m_df[["open", "high", "low", "close"]].dropna(how="all")
    if df.index.tz is None:
        raise ValueError("raw_1m_df must have a tz-aware UTC index")
    lab = broker_day(df.index)
    bars = df.groupby(lab).agg({"open": "first", "high": "max", "low": "min", "close": "last"})
    first = pd.Series(df.index, index=df.index).groupby(lab).first()
    # 4-hour bars counted from each broker day's start (17:00 America/New_York): six per day
    ny = df.index.tz_convert("America/New_York") + pd.Timedelta(hours=7)
    mos = (ny - ny.normalize()) // pd.Timedelta(minutes=int(p["tf_minutes"]))
    b4 = df.groupby([lab, np.asarray(mos)]).agg({"high": "max", "low": "min", "close": "last"})
    atr4 = _rma(_tr(b4["high"], b4["low"], b4["close"]), int(p["renko_atr"]))
    last4 = pd.DataFrame({"h4_high": b4["high"], "h4_low": b4["low"], "h4_atr": atr4})
    day = last4.index.get_level_values(0)
    last4 = last4[~day.duplicated(keep="last")]        # the day's last 4-hour bar
    last4.index = last4.index.get_level_values(0)
    bars = bars.join(last4)
    bars.index = pd.DatetimeIndex(first.loc[bars.index].values)   # each bar stamped with its first minute
    if bars.index.tz is None:
        bars.index = bars.index.tz_localize("UTC")
    return bars


def _nmax(a, b):
    return np.nan if (np.isnan(a) or np.isnan(b)) else max(a, b)


def _nmin(a, b):
    return np.nan if (np.isnan(a) or np.isnan(b)) else min(a, b)


def _vstop(src, atr, mult):
    """Pine's volatility-stop block as written (nz seeds: the first max / min compare with 0)."""
    sv, av = src.to_numpy(dtype=float), atr.to_numpy(dtype=float)
    m = len(sv)
    vstop = np.full(m, np.nan)
    mx_prev = mn_prev = 0.0
    up_prev = True
    for i in range(m):
        mx1 = _nmax(mx_prev, sv[i])
        mn1 = _nmin(mn_prev, sv[i])
        stop = mx1 - mult * av[i] if up_prev else mn1 + mult * av[i]
        vp = vstop[i - 1] if i >= 1 and not np.isnan(vstop[i - 1]) else 0.0
        v1 = _nmax(vp, stop) if up_prev else _nmin(vp, stop)
        is_up = bool(sv[i] - v1 >= 0) if not np.isnan(v1) else False
        changed = is_up != up_prev
        mx = sv[i] if changed else mx1
        mn = sv[i] if changed else mn1
        vstop[i] = ((mx - mult * av[i]) if is_up else (mn + mult * av[i])) if changed else v1
        mx_prev = 0.0 if np.isnan(mx) else mx
        mn_prev = 0.0 if np.isnan(mn) else mn
        up_prev = is_up
    return pd.Series(vstop, index=src.index)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    o, h, lo, c = (bars_df[k] for k in ("open", "high", "low", "close"))
    src = (o + h + lo + c) / 4
    atr = _rma(_tr(h, lo, c), int(p["vlen"]))
    va, vb, vc = (_vstop(src, atr, float(p[k])) for k in ("mult_a", "mult_b", "mult_c"))
    vlong = ((c > va) & (c > vb) & (c > vc) & (va > vb) & (va > vc) & (vb > vc)).to_numpy()
    vclose = ((c < va) & (c.shift(1) >= va.shift(1))).to_numpy()
    hh, ll, a4 = (bars_df[k].to_numpy(dtype=float) for k in ("h4_high", "h4_low", "h4_atr"))
    cv = c.to_numpy(dtype=float)
    m = len(cv)
    upv, dnv = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    ru_p = rd_p = np.nan
    with np.errstate(invalid="ignore"):
        for i in range(m):
            if np.isnan(ru_p):
                ru = (hh[i] + ll[i]) / 2 + a4[i] / 2
                rd = (hh[i] + ll[i]) / 2 - a4[i] / 2
            else:
                ru, rd = ru_p, rd_p
            hb = ru - rd if (np.isnan(ru_p) or np.isnan(rd_p)) else ru_p - rd_p
            for k in (3, 2, 1):
                if cv[i] >= ru_p + hb * k:
                    upv[i] = True
                    ru, rd = ru_p + a4[i] * k, ru_p + a4[i] * (k - 1)
                    break
            else:
                for k in (3, 2, 1):
                    if cv[i] <= rd_p - hb * k:
                        dnv[i] = True
                        rd, ru = rd_p - a4[i] * k, rd_p - a4[i] * (k - 1)
                        break
            ru_p, rd_p = ru, rd
    le, lx = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    pos = 0
    for i in range(m):
        if pos == 1 and (vclose[i] or dnv[i]):
            lx[i] = True
            pos = 0
        elif pos == 0 and vlong[i] and upv[i]:
            le[i] = True
            pos = 1
    ix = bars_df.index
    false = pd.Series(False, index=ix)
    return pd.Series(le, index=ix), pd.Series(lx, index=ix), false, false.copy()


def portfolio_kwargs(**params):
    return {}
