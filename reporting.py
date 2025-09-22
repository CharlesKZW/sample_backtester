
from typing import List, Tuple
import statistics, math, os
import matplotlib.pyplot as plt

def compute_returns(equity_curve: List[Tuple[object, float]]) -> List[float]:
    rets: List[float] = []
    for i in range(1, len(equity_curve)):
        prev = equity_curve[i-1][1]; curr = equity_curve[i][1]
        rets.append((curr - prev) / prev if prev > 0 else 0.0)
    return rets

def sharpe_ratio(returns: List[float], risk_free: float = 0.0, periods_per_year: int = 252*78) -> float:
    if len(returns) < 2: return 0.0
    mu = statistics.fmean(returns) - risk_free / periods_per_year
    sd = statistics.pstdev(returns)
    return 0.0 if sd == 0 else (mu / sd) * math.sqrt(periods_per_year)

def max_drawdown(equity_curve: List[Tuple[object, float]]) -> float:
    peak = float("-inf"); mdd = 0.0
    for _, v in equity_curve:
        peak = max(peak, v)
        if peak > 0: mdd = min(mdd, (v - peak) / peak)
    return mdd

def ascii_sparkline(values: List[float], width: int = 60) -> str:
    if not values: return ""
    stride = max(1, len(values)//width)
    vals = values[::stride]; lo, hi = min(vals), max(vals); blocks = "▁▂▃▄▅▆▇█"
    out = []; 
    for v in vals:
        idx = 0 if hi == lo else int((v - lo) / (hi - lo) * (len(blocks) - 1))
        out.append(blocks[idx])
    return "".join(out)

def _save_equity_plot(equity_curve: List[Tuple[object, float]], outpath: str):
    xs = [t for t, _ in equity_curve]; ys = [v for _, v in equity_curve]
    fig = plt.figure(); plt.plot(xs, ys); plt.title("Equity Curve")
    plt.xlabel("Time"); plt.ylabel("Portfolio Value")
    fig.autofmt_xdate(); plt.tight_layout(); plt.savefig(outpath); plt.close(fig)

def generate_markdown_report(output_dir: str, engine) -> str:
    os.makedirs(output_dir, exist_ok=True)
    eq_png = os.path.join(output_dir, "equity.png")
    _save_equity_plot(engine.portfolio_values, eq_png)
    returns = compute_returns(engine.portfolio_values)
    starting = engine.portfolio_values[0][1] if engine.portfolio_values else float("nan")
    ending = engine.portfolio_values[-1][1] if engine.portfolio_values else float("nan")
    total = (ending / starting - 1.0) if engine.portfolio_values else 0.0
    sr = sharpe_ratio(returns); mdd = max_drawdown(engine.portfolio_values)
    spark = ascii_sparkline([v for _, v in engine.portfolio_values])
    lines = []
    lines += ["# Performance Report\n","## Summary Metrics\n","| Metric | Value |\n|---|---|\n"]
    lines += [f"| Starting Equity | {starting:.2f} |\n", f"| Ending Equity | {ending:.2f} |\n",
              f"| Total Return | {total:.2%} |\n", f"| Sharpe (per-tick scaled) | {sr:.2f} |\n",
              f"| Max Drawdown | {mdd:.2%} |\n"]
    lines += ["\n## Equity Curve\n", f"![Equity]({os.path.basename(eq_png)})\n",
              "\n## ASCII Sparkline\n```\n", spark + "\n```\n",
              "## Executions\n", f"- Executed orders: {len(engine.executed_history)}\n",
              f"- Failed orders: {len(engine.failed_history)}\n", "\n### First 5 Executions\n```\n"]
    for rec in engine.executed_history[:5]: lines.append(str(rec) + "\n")
    lines.append("```\n")
    out_md = os.path.join(output_dir, "performance.md")
    with open(out_md, "w") as f: f.write("".join(lines))
    return out_md
