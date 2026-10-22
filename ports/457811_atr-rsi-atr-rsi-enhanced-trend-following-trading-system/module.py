"""UT Bot line (key 1, ATR 10) crossings with an RSI 14 side filter, no bar size in the source: the close crossing over the line with the RSI over 50 goes long, under it with the RSI under 50 goes short; a close 0.2 % beyond the latest signal close either way closes; reversing.
Port of FMZ strategy #457811 "ATR-RSI增强型趋势追踪交易系统-ATR-RSI-Enhanced-Trend-Following-Trading-System" (UT Bot Alerts - Non-Repainting with RSI Filter).

FMZ source id: 457811

Source
    https://www.fmz.com/strategy/457811 (PineScript v5, FMZ last modified 2024-07-26 17:35:31).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 157-257), key value 1; ATR 10; Heikin Ashi off; RSI 14 vs 50; exit band 0.2 % of the signal close
    UT line as the classic UT Bot;  src > line and crossover(src, line) and rsi > 50 -> entry Buy (targets = src x 1.002 / 0.998);  the mirror and rsi < 50 -> entry Sell
    long and (src >= upper target or src <= lower target) -> exit(limit = that target);  short likewise

Interpretation choices (Pine rules in SURVEY_README.md)
    * barstate.isconfirmed holds on every historical bar. The exits are sent at the bar close once
      the close has moved 0.2 % from the latest signal's close, as a limit at that level, which is
      then marketable: ported as a bar-close test filled at the next open (the limit's own price is not
      modelled), followed in a loop with the levels reset by every signal. The source has no backtest
      header and names no bar size: FREQ = "bar_size_pending" (rule 1); precompute builds the bars with
      the house bar_sizes.build_bars with the driver's bar_size. REVERSAL INTENDED. No sizing code.

Admission criteria
    1 fits the interface: PASS, bar-close orders; the target exits as close tests.
    2 generic: PASS, UT Bot crossings with an RSI filter.
    3 crypto-exchange-only: no (no exchange named).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (8 trials), before any backtest.
    6 near-duplicates: ND457811 (2 members, best partner #458056, Jaccard 0.744); ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
REVERSAL INTENDED.

Marks: bar_size_pending
"""
import numpy as np
import pandas as pd

NAME = "fmz_457811_ut_bot_rsi_filter_band_exit_reversal"
FAMILY = "atr_trailing_line"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "bar_size_pending"  # the source names no bar size (rule 1)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "key": [1.0, 2.0],
    "atr_len": [10, 14],
    "band_pct": [0.002, 0.01],
}
DEFAULT_PARAMS = {"key": 1.0, "atr_len": 10, "band_pct": 0.002, "rsi_len": 14}


def precompute(raw_1m_df, symbol_key, **params):
    import bar_sizes                      # the house builder (mining\bar_sizes.py), on the desktop's path
    return bar_sizes.build_bars(raw_1m_df, params["bar_size"])


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
    c = bars_df["close"]
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
    c1s, l1 = c.shift(1), ln.shift(1)
    buy = ((c > ln) & (c1s <= l1) & (r > 50)).to_numpy()      # src > line and crossover(src, line)
    sell = ((ln > c) & (l1 <= c1s) & (r < 50)).to_numpy()     # src < line and crossover(line, src)
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
            cur = 0                               # the target exit acts on the trade held into the bar
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
