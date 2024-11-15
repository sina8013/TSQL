import pytest
from tsql import TSQL


def test_example():
    obj = TSQL(
        api_id="123",
        api_hash="abc",
        sessionName="test",
        chanellInviteLink="link",
        databaseStructurePath="path",
    )
    assert obj is not None
