def test_equal_or_not_equal():
    assert 3 == 3
    assert 3 != 1

def test_is_instance():
    assert isinstance('This is a string', str)
    assert not isinstance('10', int)

def test_boolean():
    validated = True
    assert validated is True
    assert ('hello' == 'world') is False

def test_type():
    assert type('Hello' is str)
    assert type('World' is not int)

def test_greater_and_less_than():
    assert 7 > 3
    assert 4 < 10

def test_list():
    num_list = [1,2,3,4,5]
    any_list = [False, False]
    assert 1 in num_list
    assert 7 not in num_list
    # all elements of the list are truthy, hence the
    # below test passes
    assert all(num_list) 
    # all elements of the 'any_list' are falsy, hence
    # the below test with `not` passes.
    assert not any(any_list)

