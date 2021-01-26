# Octue python standards

### One-line if/else statements
One-line `if/else` statements should be avoided except when dealing with default mutable arguments. For example,
```python
iterations = iterations if mode == "iteration" else None
```
should be avoided, but the following is fine to use:
```python
def my_function(a, b=None):
    b = b if b is None else []  # Note that this can usually (but not always) be written better as b = b or []
```

The reason for avoiding these statements is that the test coverages of the `if` and `else` conditions are not measured 
independently unless they are on their own lines, resulting in misleading coverage statistics. 
