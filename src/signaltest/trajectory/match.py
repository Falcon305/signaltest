def match_score(baseline, candidate, ignore_keys=()):
    steps = max(len(baseline), len(candidate))
    if steps == 0:
        return 1.0
    matched = sum(
        b.tool == c.tool and _without(b.args, ignore_keys) == _without(c.args, ignore_keys)
        for b, c in zip(baseline, candidate)
    )
    return matched / steps


def _without(args, ignore_keys):
    return {k: v for k, v in args.items() if k not in ignore_keys}
