import pytest
from magic_constants import Constant


class Root(Constant):
    Branch_A: "Branch_A"
    Branch_B: "Branch_B"


class Branch_A(Root):
    Leaf_AA: "Leaf_AA"


class Branch_B(Root):
    Leaf_BB: "Leaf_BB"


class Leaf_A(Root):
    value = "a"


class Leaf_AA(Branch_A):
    value = "aa"


class Leaf_BB(Branch_B):
    value = "bb"


def test_leaf():
    assert Leaf_A() == Leaf_A()
    assert Leaf_A().value == "a"
    assert type(Leaf_A()) is Leaf_A

    assert str(Leaf_A()) == "a"
    assert str(type(Leaf_A())) == "Root.Leaf_A('a')"

    with pytest.raises(ValueError) as e_info:
        Leaf_A("b")
    assert e_info.match("'b' cannot be validated as type Leaf_A. Expected 'a'")

    assert Leaf_AA() == Leaf_AA()
    assert Leaf_AA().value == "aa"
    assert type(Leaf_AA()) is Leaf_AA


def test_branch():
    assert Root.Branch_A is Branch_A
    assert Root.Branch_A.Leaf_A is Leaf_A

    assert Root("a") == Leaf_A()
    assert Root("aa") == Root.Branch_A("aa") == Leaf_AA()
    assert Root("bb") == Root.Branch_B("bb") == Leaf_BB()

    with pytest.raises(ValueError) as e_info:
        assert Root.Branch_B("aa")
    assert e_info.match("'aa' is not a valid Branch_B. Expected Branch_Bs: 'bb'")

    with pytest.raises(NotImplementedError) as e_info:
        # shouldn't be able to implement abstract class
        Branch_A()
    assert e_info.match("Abstract Root 'Branch_A' cannot be instantiated!")
