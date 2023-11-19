quick_sort = (
    lambda s: s
    if len(s) <= 1
    else quick_sort([x for x in s[1:] if x <= s[0]])
    + [s[0]]
    + quick_sort([x for x in s[1:] if x > s[0]])
)
