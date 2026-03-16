import pytest

from parseidf import parse


def test_single_object_no_values():
    idf = "Version;"
    expected = {"VERSION": [["Version"]]}
    assert parse(idf) == expected


def test_single_object_with_values():
    idf = "Material, Brick, 0.5, 0.8;"
    expected = {"MATERIAL": [["Material", "Brick", "0.5", "0.8"]]}
    assert parse(idf) == expected


def test_multiple_objects_same_type():
    idf = "Zone, LivingRoom, 20;\nZone, Kitchen, 15;"
    expected = {
        "ZONE": [
            ["Zone", "LivingRoom", "20"],
            ["Zone", "Kitchen", "15"],
        ]
    }
    assert parse(idf) == expected


def test_multiple_objects_different_types():
    idf = "Building, MyHouse;\nZone, Bedroom, 12;"
    expected = {
        "BUILDING": [["Building", "MyHouse"]],
        "ZONE": [["Zone", "Bedroom", "12"]],
    }
    assert parse(idf) == expected


def test_comments_are_ignored():
    idf = "! This is a comment\nMaterial, Wood, 0.3, 0.6; ! Another comment"
    expected = {"MATERIAL": [["Material", "Wood", "0.3", "0.6"]]}
    assert parse(idf) == expected


def test_whitespace_and_newlines():
    idf = "  Material ,  Wood , 0.3 , 0.6 ;\n\nZone , Bedroom , 12 ;"
    expected = {
        "MATERIAL": [["Material", "Wood", "0.3", "0.6"]],
        "ZONE": [["Zone", "Bedroom", "12"]],
    }
    assert parse(idf) == expected


def test_object_with_asterisk():
    idf = "Schedule, *, *, *;"
    expected = {"SCHEDULE": [["Schedule", "*", "*", "*"]]}
    assert parse(idf) == expected


@pytest.mark.parametrize(
    "idf",
    [
        pytest.param("Material, Brick, 0.5, 0.8", id="missing_semicolon"),
        pytest.param("Material, Brick, 0.5, 0.8; $", id="illegal_character"),
        pytest.param("", id="empty_input"),
    ],
)
def test_syntax_errors(idf):
    with pytest.raises(SyntaxError):
        parse(idf)


def test_object_with_only_name_and_semicolon():
    idf = "Building;"
    expected = {"BUILDING": [["Building"]]}
    assert parse(idf) == expected
