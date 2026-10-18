"""Four reversal rules on one position, 3-minute bars: (1) the close crossing over all of the EMA 20 / 50 / 100 / 200 on one bar while over the EMA 400 and 800 buys; (2) an RSI 14 over 90 sells and under 10
buys; (3) after a sudden RSI jump of more than 10 points, the position is taken the other way ten bars later if price then confirms; (4) the SMA of the RSI crossing over 60 buys and
under 40 sells.
Port of FMZ strategy #436008 "基于RSI-SMA的突发性买卖策略SMA-RSI-Sudden-Buy-Sell-Strategy" (sma RSI & sudden buy and sell Strategy v1).

FMZ source id: 436008

Source
    https://www.fmz.com/strategy/436008 (PineScript v5, FMZ last modified 2023-12-20 17:33:04).
    Verbatim copy: original_source.md. Read 2026-10-18 (FMZ-C).

Original signal (original_source.md lines 160-317), RSI 14; EMA 20 / 50 / 100 / 200 / 400 / 800; jump 10 points, wait 10 bars; SMA of RSI against 60 / 40
    (1) co_x = crossover(price, ema_x) for x = 20, 50, 100, 200 on the same bar and price > ema800 and ema400 -> close Sell, entry Buy
    (2) rsi > 90 -> close Buy, entry Sell;  rsi < 10 -> close Sell, entry Buy
    (3) rsi - rsi[1] > 10 and highest(price, 20) > price -> sudB = 1, sudBC = close, after 10 bars: if sudBC < price -> close Sell, entry Buy;  rsi[1] - rsi > 10 -> sudS = 1, ..., after 10 bars: if sudSC > price -> close Buy, entry Sell
    (4) crossover(sma(rsi, 14), 60) -> close Sell, entry Buy;  crossunder(sma(rsi, 14), 40) -> close Buy, entry Sell

Interpretation choices (Pine rules in SURVEY_README.md)
    * Each co_x flag is overwritten every bar, so rule (1) needs the four crossings on ONE bar (rare). The
      sudden-move counters follow the script (the count starts the bar after the jump and a
      further jump only refreshes the stored close). A close followed by an entry in the same rule is a
      reversal; the orders of one bar are filled in the script's call order at the next open.
      REVERSAL INTENDED. FREQ = "3min" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, average crossings, RSI levels and a jump rule.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_436008_rsi_sma_sudden_reversals"
FAMILY = "rsi_oscillator"  # proposed 2026-10-18 (FMZ-C), user to confirm
FREQ = "3min"  # backtest header period: 3m
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "length": [14, 7],
    "bars": [10, 5],
}
DEFAULT_PARAMS = {"length": 14, "bars": 10, "inst_length": 10, "lookback": 20}


def _resample(raw_1m_df, freq):
    ohlc = raw_1m_df[["open", "high", "low", "close"]]
    bars = ohlc.resample(freq, label="left", closed="left").agg(
        {"open": "first", "high": "max", "low": "min", "close": "last"})
    bars = bars.dropna(how="all")  # an empty period is not a bar; never forward-filled
    if bars.index.tz is None:
        raise ValueError("raw_1m_df must have a tz-aware UTC index")
    return bars


def precompute(raw_1m_df, symbol_key, **params):
    return _resample(raw_1m_df, FREQ)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    c = bars_df["close"]
    n = int(p["length"])
    ch = c.diff()
    up = ch.clip(lower=0).ewm(alpha=1 / n, adjust=False).mean()
    dn = (-ch.clip(upper=0)).ewm(alpha=1 / n, adjust=False).mean()
    rsi = (100 - 100 / (1 + up / dn)).where(dn != 0, 100.0).where(up.notna())
    emas = {k: c.ewm(span=k, adjust=False).mean() for k in (20, 50, 100, 200, 400, 800)}

    def cx(k):
        return ((c > emas[k]) & (c.shift(1) <= emas[k].shift(1))).fillna(False).to_numpy()

    rule1 = cx(20) & cx(50) & cx(100) & cx(200) & ((c > emas[800]) & (c > emas[400])).fillna(False).to_numpy()
    r1 = rsi.shift(1)
    buy_diff, sell_diff = (rsi - r1).to_numpy(), (r1 - rsi).to_numpy()
    hi2 = c.rolling(int(p["lookback"])).max().to_numpy()
    cv = c.to_numpy(dtype=float)
    sm = rsi.rolling(n).mean()
    coo = ((sm > 60) & (sm.shift(1) <= 60)).fillna(False).to_numpy()
    cuu = ((sm < 40) & (sm.shift(1) >= 40)).fillna(False).to_numpy()
    rv = rsi.to_numpy()
    inst, nb = float(p["inst_length"]), int(p["bars"])
    m = len(cv)
    held = np.zeros(m, dtype=np.int8)
    pos = 0
    ops = []
    sud_b = sud_s = 0
    sud_bc = sud_sc = np.nan
    cnt_b = cnt_s = 0
    for i in range(m):
        if i > 0:                            # fills at this bar's open, in the order the script sent them
            for op in ops:
                if op == "cS" and pos == -1:
                    pos = 0
                elif op == "cB" and pos == 1:
                    pos = 0
                elif op == "eB" and pos <= 0:
                    pos = 1
                elif op == "eS" and pos >= 0:
                    pos = -1
        held[i] = pos
        ops = []
        if rule1[i]:
            ops += ["cS", "eB"]
        if rv[i] > 90:
            ops += ["cB", "eS"]
        if rv[i] < 10:
            ops += ["cS", "eB"]
        if sud_b == 1:
            cnt_b += 1
        if sud_s == 1:
            cnt_s += 1
        if buy_diff[i] > inst and hi2[i] > cv[i]:
            sud_b, sud_bc = 1, cv[i]
        if sell_diff[i] > inst:
            sud_s, sud_sc = 1, cv[i]
        if cnt_b == nb:
            if sud_bc < cv[i]:
                ops += ["cS", "eB"]
            cnt_b, sud_b = 0, 0
        if cnt_s == nb:
            if sud_sc > cv[i]:
                ops += ["cB", "eS"]
            cnt_s, sud_s = 0, 0
        if coo[i]:
            ops += ["cS", "eB"]
        if cuu[i]:
            ops += ["cB", "eS"]
    nxt = np.concatenate((held[1:], held[-1:]))
    ix = bars_df.index
    return (pd.Series((nxt == 1) & (held != 1), index=ix), pd.Series((nxt == 0) & (held == 1), index=ix),
            pd.Series((nxt == -1) & (held != -1), index=ix), pd.Series((nxt == 0) & (held == -1), index=ix))


def portfolio_kwargs(**params):
    return {}
