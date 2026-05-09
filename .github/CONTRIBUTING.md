# `numba-instrument` Development

Pushing a tag will kick off a new pip package:

1.  Make sure all tests pass after last PR merged into main

2.  Tag with the next version number and push the tag:

```
uv run cz bump
git push origin main --tags
```

3.  This should kick off a deploy through the `ci.yaml` action.

