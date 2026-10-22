"""RSI 7 extremes against the EMA 50, daily bars: a close under the EMA 50 with the RSI 7 of the previous closes under 20 on an up close goes long, with a stop ATR 14 + body under and a target 1.2 times that over the signal close; the mirror (over the EMA, RSI over 80, a down close) goes short only from flat, with levels set from the bar's high; reversing for the long side.
Port of FMZ strategy #453238 "EMA与RSI交叉策略-EMA-RSI-Crossover-Strategy" (EMA RSI Cross).

FMZ source id: 453238

Source
    https://www.fmz.com/strategy/453238 (PineScript v5, FMZ last modified 2024-06-03 11:08:30).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 94-167), RSI 7 of close[1], levels 20 / 80; EMA 50; ATR 14; distance ATR + |close - open|; target 1.2 x distance; margins 100 / 100
    ema > close and rsi < 20 and opentrades >= 0 and close > close[1] -> entry Long, exit(stop = close - d, limit = close + 1.2 d)
    ema < close and rsi > 80 and opentrades <= 0 and close < close[1] -> entry Short, exit(stop = high + d, limit = high - 1.2 d)

Interpretation choices (Pine rules in SURVEY_README.md)
    * opentrades >= 0 always holds, so a long signal also reverses a short; opentrades <= 0 means flat,
      so shorts open only from flat. The levels are fixed on the signal bar: ported as fractions of
      the signal close applied to the fill, followed in the loop on each bar's low / high so the flat
      test lines up. A short whose target (high - 1.2 d) sits at or over the signal close would be
      filled at once with its entry, so that signal is sent as no trade. A repeat signal inside a trade
      re-issues the levels, which stops() cannot express: the opening levels are kept and the module
      is marked trailing_stop_pending (as #434428). REVERSAL INTENDED. Stop module: portfolio_kwargs {}
      (driver D4). Stops on 1-day bars: mark coarse_bar_stop. The margin settings are sizing. FREQ =
      "1D" from the backtest header (broker days).

Admission criteria
    1 fits the interface: PASS, bar-close orders; the signal-bar levels as fractions; re-issued levels pending (mark).
    2 generic: PASS, RSI extremes against the EMA with ATR / body brackets.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: the margin settings stored.
    5 ranges declared: GRID below (8 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
REVERSAL INTENDED.

Marks: coarse_bar_stop, trailing_stop_pending
"""
import numpy as np
import pandas as pd

NAME = "fmz_453238_rsi7_extreme_vs_ema50_atr_body_bracket"
FAMILY = "rsi_oscillator"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "rsi_len": [7, 14],
    "ema_len": [50, 100],
    "tp_mult": [1.2, 2.0],
}
DEFAULT_PARAMS = {"rsi_len": 7, "ema_len": 50, "tp_mult": 1.2, "atr_len": 14, "os": 20.0, "ob": 80.0}


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
    return 100 - 100 / (1 + up / dn)


def _atr(bars_df, n):
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    pc = c.shift(1)
    tr = pd.concat([h - lo, (h - pc).abs(), (lo - pc).abs()], axis=1).max(axis=1)
    return _rma(tr, int(n))


def _run(bars_df, p):
    o, h, lo, c = (bars_df[k] for k in ("open", "high", "low", "close"))
    r = _rsi(c.shift(1), int(p["rsi_len"]))
    ema = c.ewm(span=int(p["ema_len"]), adjust=False).mean()
    d = _atr(bars_df, p["atr_len"]) + (c - o).abs()
    k = float(p["tp_mult"])
    buy = ((ema > c) & (r < float(p["os"])) & (c > c.shift(1))).to_numpy()
    sell = ((ema < c) & (r > float(p["ob"])) & (c < c.shift(1))).to_numpy()
    l_sl, l_tp = (d / c).to_numpy(), (k * d / c).to_numpy()
    s_sl, s_tp = ((h + d - c) / c).to_numpy(), ((c - (h - k * d)) / c).to_numpy()
    ov = o.to_numpy(dtype=float)
    hv, lv = h.to_numpy(dtype=float), lo.to_numpy(dtype=float)
    m = len(ov)
    le, se = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    sl_a, tp_a = np.full(m, np.nan), np.full(m, np.nan)
    pos, entry_i, slf, tpf = 0, -1, np.nan, np.nan
    for i in range(m):
        if pos == 1 and i >= entry_i and (lv[i] <= ov[entry_i] * (1 - slf) or hv[i] >= ov[entry_i] * (1 + tpf)):
            pos = 0
        elif pos == -1 and i >= entry_i and (hv[i] >= ov[entry_i] * (1 + slf) or lv[i] <= ov[entry_i] * (1 - tpf)):
            pos = 0
        if i + 1 >= m:
            continue
        if buy[i] and pos != 1 and l_sl[i] > 0:
            le[i], pos, entry_i, slf, tpf = True, 1, i + 1, l_sl[i], l_tp[i]
            sl_a[i], tp_a[i] = slf, tpf
        elif sell[i] and pos == 0 and s_tp[i] > 0 and s_sl[i] > 0:
            se[i], pos, entry_i, slf, tpf = True, -1, i + 1, s_sl[i], s_tp[i]
            sl_a[i], tp_a[i] = slf, tpf
    return le, se, sl_a, tp_a


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    le, se, _, _ = _run(bars_df, p)
    ix = bars_df.index
    false = pd.Series(False, index=ix)
    return pd.Series(le, index=ix), false, pd.Series(se, index=ix), false.copy()


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    _, _, sl_a, tp_a = _run(bars_df, p)
    ix = bars_df.index
    return {"sl_stop": pd.Series(sl_a, index=ix).shift(1), "tp_stop": pd.Series(tp_a, index=ix).shift(1)}


def portfolio_kwargs(**params):
    return {}
