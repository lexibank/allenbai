def test_valid(cldf_dataset, cldf_logger):
    assert cldf_dataset.validate(log=cldf_logger)
    assert any(f['Form'] == 'mi³⁵zɔ²¹' for f in cldf_dataset['FormTable'])
    assert len(list(cldf_dataset['FormTable'])) == 4546
