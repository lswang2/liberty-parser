# Liberty Parser

The original source is in https://codeberg.org/tok/liberty-parser

Example
```python
from liberty.parser import parse_liberty
library = parse_liberty(open(liberty_file).read())

print(str(library))
```
