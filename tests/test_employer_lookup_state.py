from app import normalize_query_param_value


def test_normalize_query_param_value_scalar():
    assert normalize_query_param_value("citigroup") == "citigroup"


def test_normalize_query_param_value_list():
    assert normalize_query_param_value(["amazon", "extra"]) == "amazon"


def test_normalize_query_param_value_empty_list():
    assert normalize_query_param_value([]) == ""


def test_normalize_query_param_value_none():
    assert normalize_query_param_value(None) == ""
