"""Run the python blocks of a docs page in order, in one namespace. Exit 1 on the first error."""
import re
import sys
import traceback

page = sys.argv[1]
blocks = re.findall(r"^```python\n(.*?)^```$", open(page, encoding="utf8").read(), flags=re.S | re.M)
namespace = {"__name__": "__doc_example__"}
for n, block in enumerate(blocks, 1):
    try:
        exec(compile(block, f"{page}:block{n}", "exec"), namespace)
    except Exception:
        traceback.print_exc()
        sys.exit(f"{page}: python block {n} of {len(blocks)} fails")
print(f"OK {page}: {len(blocks)} python blocks")
