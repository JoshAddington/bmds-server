from copy import deepcopy
import json
import jsonschema
import pytest

from jobrunner import validators


@pytest.fixture
def complete_continuous():
    return {
        'bmds_version': 'BMDS2601',
        'dataset_type': 'C',
        'datasets': [
            {
                'id': 123,
                'doses': [0, 10, 50, 150, 400],
                'ns': [111, 142, 143, 93, 42],
                'responses': [2.112, 0, 1.956, 1.587, 1.254],
                'stdevs': [0.235, 0, 0.231, 0.263, 0.159]
            }
        ]
    }


@pytest.fixture
def complete_dichotomous():
    return {
        'bmds_version': 'BMDS2601',
        'dataset_type': 'D',
        'datasets': [
            {
                'id': 123,
                'doses': [0, 1.96, 5.69, 29.75],
                'ns': [75, 49, 50, 49],
                'incidences': [5, 0, 3, 14]
            },
        ]
    }


def test_invalid_json():
    # invalid JSON
    with pytest.raises(ValueError):
        validators.validate_input("{")


def test_base_validator(complete_continuous):
    # check validity
    try:
        jsonschema.validate(complete_continuous, validators.base_schema)
    except jsonschema.exceptions.ValidationError:
        pytest.fail('Should be valid.')

    # missing required field check
    data = deepcopy(complete_continuous)
    data.pop('bmds_version')
    with pytest.raises(jsonschema.exceptions.ValidationError):
        jsonschema.validate(data, validators.base_schema)


def test_continuous_validator(complete_continuous):
    # check that continous validators work
    datasets = complete_continuous['datasets']
    # check validity
    try:
        jsonschema.validate(datasets, validators.continuous_dataset_schema)
    except jsonschema.exceptions.ValidationError:
        pytest.fail('Should be valid.')

    # missing required field check
    data = deepcopy(datasets)
    data[0].pop('stdevs')
    with pytest.raises(jsonschema.exceptions.ValidationError):
        jsonschema.validate(data, validators.continuous_dataset_schema)

    # n>0 check
    data = deepcopy(datasets)
    data[0]['ns'][1] = 0
    with pytest.raises(jsonschema.exceptions.ValidationError):
        jsonschema.validate(data, validators.dichotomous_dataset_schema)


def test_dichotomous_validator(complete_dichotomous):
    # check that dichotomous validators work
    datasets = complete_dichotomous['datasets']
    # check validity
    try:
        jsonschema.validate(datasets, validators.dichotomous_dataset_schema)
    except jsonschema.exceptions.ValidationError:
        pytest.fail('Should be valid.')

    # missing required field check
    data = deepcopy(datasets)
    data[0].pop('ns')
    with pytest.raises(jsonschema.exceptions.ValidationError):
        jsonschema.validate(data, validators.dichotomous_dataset_schema)

    # n>0 check
    data = deepcopy(datasets)
    data[0]['ns'][1] = 0
    with pytest.raises(jsonschema.exceptions.ValidationError):
        jsonschema.validate(data, validators.dichotomous_dataset_schema)


def test_dataset_ids(complete_continuous, complete_dichotomous):
    # Check that commonly used IDs can be used.
    sets = [
        (complete_continuous['datasets'], validators.continuous_dataset_schema),
        (complete_dichotomous['datasets'], validators.dichotomous_dataset_schema)
    ]
    for datasets, validator in sets:
        # check missing ID
        data = deepcopy(datasets)
        data[0].pop('id')
        jsonschema.validate(data, validator)

        # check string ID
        data = deepcopy(datasets)
        data[0]['id'] = 'string'
        jsonschema.validate(data, validator)

        # check int ID
        data = deepcopy(datasets)
        data[0]['id'] = 123  # int
        jsonschema.validate(data, validator)

        # check float id
        data = deepcopy(datasets)
        data[0]['id'] = 123.1  # float
        with pytest.raises(jsonschema.exceptions.ValidationError):
            jsonschema.validate(data, validator)


def test_models(complete_continuous):
    # Check models can be specified
    cmodels = [
        {'name': 'Exponential-M2'},
        {'name': 'Exponential-M3'}
    ]

    dmodels = [
        {'name': 'Logistic'},
        {'name': 'LogLogistic'}
    ]

    # complete check
    data = deepcopy(complete_continuous)
    data['models'] = cmodels
    try:
        validators.validate_input(json.dumps(data))
    except ValueError:
        pytest.fail('Should be valid.')

    data = deepcopy(complete_continuous)
    data['models'] = dmodels
    with pytest.raises(ValueError):
        validators.validate_input(json.dumps(data))

    # continuous
    try:
        jsonschema.validate(cmodels, validators.c_model_schema)
    except jsonschema.exceptions.ValidationError:
        pytest.fail('Should be valid.')

    with pytest.raises(jsonschema.exceptions.ValidationError):
        jsonschema.validate(dmodels, validators.c_model_schema)

    # dichotomous
    try:
        jsonschema.validate(dmodels, validators.d_model_schema)
    except jsonschema.exceptions.ValidationError:
        pytest.fail('Should be valid.')

    with pytest.raises(jsonschema.exceptions.ValidationError):
        jsonschema.validate(cmodels, validators.d_model_schema)