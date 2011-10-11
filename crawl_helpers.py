def FilterListBySuffix(items, suffixes):
    """Filters a list .

    Arguments:
      items -- a list of strings.
      suffixes -- the allowed suffixes.

    Returns:
      A list containing only the items whose suffix is contained in suffixes.
    """
    new_list = []
    for item in items:
        for suffix in suffixes:
            if item.endswith(suffix):
                new_list.append(item)
                continue
    return new_list
