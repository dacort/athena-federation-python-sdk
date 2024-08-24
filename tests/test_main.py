from athena_federation import main


def test_main(capsys):
    main()
    captured = capsys.readouterr()
    assert "Hello from athena_federation!" in captured.out
    assert "Arguments: " in captured.out
    assert "Environment:  " in captured.out
