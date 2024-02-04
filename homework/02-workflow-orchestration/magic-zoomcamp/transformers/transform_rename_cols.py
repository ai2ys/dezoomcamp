import re
if 'transformer' not in globals():
    from mage_ai.data_preparation.decorators import transformer
if 'test' not in globals():
    from mage_ai.data_preparation.decorators import test


def camel_to_snake(name):
    s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', name)
    return re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1).lower()


@transformer
def transform(data, *args, **kwargs):
    original_columns = data.columns.tolist()
    data.columns = [camel_to_snake(col) for col in data.columns]
    renamed_columns = {original: new for original, new in zip(original_columns, data.columns) if original != new}

    print(f'{len(renamed_columns)} columns have been renamed.')
    for original, new in renamed_columns.items():
        print(f'Original: {original} --> New: {new}')
    return data


@test
def test_output(output, *args) -> None:
    """
    Template code for testing the output of the block.
    """
    assert output is not None, 'The output is undefined'
