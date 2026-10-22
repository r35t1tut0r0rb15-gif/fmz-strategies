"""UT Bot line (key 1, ATR 10) crossings with an RSI 14 filter and the Donchian 20 midline side, daily bars: the close crossing over the line with the RSI over 50 and the close over the midline goes long, the mirror goes short; a close 0.2 % beyond the latest signal close either way closes; reversing.
Port of FMZ strategy #458056 "Multi Indicator Adaptive Trend Following Strategy" (UT Bot Alerts - Non-Repainting with RSI Filter and Donchian Channels).

FMZ source id: 458056

Source
    https://www.fmz.com/strategy/458056 (PineScript v5, FMZ last modified 2024-07-29 15:51:54).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 176-289), key value 1; ATR 10; Heikin Ashi off; RSI 14 vs 50; Donchian 20 midline; exit band 0.2 % of the signal close
    src > line and crossover(src, line) and rsi > 50 and src > donchian mid -> entry Buy (targets src x 1.002 / 0.998);  the mirror -> entry Sell
    long: src >= upper target -> exit(limit = target);  src <= lower target -> exit(stop = src);  short mirrored

Interpretation choices (Pine rules in SURVEY_README.md)
    * As #457811 with a Donchian 20 midline filter. The exits are sent at the bar close once the close
      has moved 0.2 % from the latest signal's close: a limit at the target (already marketable) or a
      stop at the bar's close; both are ported as a bar-close test filled at the next open (their own
      fill prices are not modelled), followed in a loop with the levels reset by every signal.
      barstate.isconfirmed holds on every historical bar. REVERSAL INTENDED. No sizing code. FREQ =
      "1D" from the backtest header (broker days).

Admission criteria
    1 fits the interface: PASS, bar-close orders; the target / stop exits as close tests.
    2 generic: PASS, UT Bot crossings with RSI and Donchian filters.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (8 trials), before any backtest.
    6 near-duplicates: ND457811 (2 members, best partner #457811, Jaccard 0.744); ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_458056_ut_bot_rsi_donchian_band_exit_reversal"
FAMILY = "atr_trailing_line"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "key": [1.0, 2.0],
    "dc_len": [20, 50],
    "band_pct": [0.002, 0.01],
}
DEFAULT_PARAMS = {"key": 1.0, "dc_len": 20, "band_pct": 0.002, "atr_len": 10, "rsi_len": 14}


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


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    nl = (float(p["key"]) * _atr(bars_df, p["atr_len"])).to_numpy()
    cv = c.to_numpy(dtype=float)
    m = len(cv)
    line = np.full(m, np.nan)
    for i in range(m):
        prev = line[i - 1] if i > 0 and not np.isnan(line[i - 1]) else 0.0
        c1 = cv[i - 1] if i > 0 else np.nan
        if np.isnan(nl[i]):
            continue                          # math.max / min with an na ATR give na
        if cv[i] > prev and c1 > prev:
            line[i] = max(prev, cv[i] - nl[i])
        elif cv[i] < prev and c1 < prev:
            line[i] = min(prev, cv[i] + nl[i])
        else:
            line[i] = cv[i] - nl[i] if cv[i] > prev else cv[i] + nl[i]
    ln = pd.Series(line, index=c.index)
    r = _rsi(c, int(p["rsi_len"]))
    n = int(p["dc_len"])
    mid = (h.rolling(n).max() + lo.rolling(n).min()) / 2
    c1s, l1 = c.shift(1), ln.shift(1)
    buy = ((c > ln) & (c1s <= l1) & (r > 50) & (c > mid)).to_numpy()
    sell = ((ln > c) & (l1 <= c1s) & (r < 50) & (c < mid)).to_numpy()
    k = float(p["band_pct"])
    le, lx, se, sx = (np.zeros(m, dtype=bool) for _ in range(4))
    pos, up_t, dn_t = 0, np.nan, np.nan
    for i in range(m):
        cur = pos
        if buy[i]:
            up_t, dn_t = cv[i] * (1 + k), cv[i] * (1 - k)
            if cur != 1:
                cur = 1
        if sell[i]:
            up_t, dn_t = cv[i] * (1 + k), cv[i] * (1 - k)
            if cur != -1:
                cur = -1
        if pos != 0 and cur == pos and (cv[i] >= up_t or cv[i] <= dn_t):
            cur = 0                               # the exit acts on the trade held into the bar
        if cur == 1 and pos != 1:
            le[i] = True
        elif cur == -1 and pos != -1:
            se[i] = True
        elif cur == 0 and pos == 1:
            lx[i] = True
        elif cur == 0 and pos == -1:
            sx[i] = True
        pos = cur
    ix = bars_df.index
    return (pd.Series(le, index=ix), pd.Series(lx, index=ix),
            pd.Series(se, index=ix), pd.Series(sx, index=ix))


def portfolio_kwargs(**params):
    return {}
