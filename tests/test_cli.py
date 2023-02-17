import pytest

from tiktok_uploader import cli

def test_cli():
    """
    Tests the CLI entry point
    """

    # Trys to see if it will run without any erros
    try:
        cli.main()
    except Exception as e:
        pytest.fail(f'CLI failed to run with error: {e}')
