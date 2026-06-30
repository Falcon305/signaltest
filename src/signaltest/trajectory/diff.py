def render_diff(baseline, candidate):
    lines = []
    for i in range(max(len(baseline), len(candidate))):
        b = baseline[i] if i < len(baseline) else None
        c = candidate[i] if i < len(candidate) else None
        if b is not None and c is not None and b.tool == c.tool and b.args == c.args:
            lines.append(f"  {_fmt(b)}")
        else:
            if b is not None:
                lines.append(f"- {_fmt(b)}")
            if c is not None:
                lines.append(f"+ {_fmt(c)}")
    return "\n".join(lines)


def _fmt(step):
    return f"{step.tool}({step.args})"
