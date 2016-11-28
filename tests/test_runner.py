from copy import deepcopy
from django.test import Client
import json
import time

from .fixtures import *  # noqa


@pytest.mark.django_db(transaction=False)
def test_d_success(complete_dichotomous):
    # BMDS execution is slow; we overload this test to check lots of things.
    data = deepcopy(complete_dichotomous)

    # use a single model for speed
    data['models'] = [
        {'name': 'Logistic'},
    ]

    # use alternative BMR definition
    data['bmr'] = {
        'type': 'Extra',
        'value': 0.25,
    }

    # submit new job
    c = Client()
    payload = json.dumps(data)
    resp = c.post('/api/job/', {'inputs': payload})
    assert resp.status_code == 201

    # poll until job complete
    url = '/api/job/{}/'.format(resp.json()['id'])
    while True:
        time.sleep(2)
        resp = c.get(url)
        if resp.json()['is_finished']:
            break

    # check alternative BMR definition
    outfile = resp.json()['outputs']['outputs'][0]['models'][0]['outfile']
    assert 'Specified effect =           0.25' in outfile

    # check parsed model output exists
    bmd = resp.json()['outputs']['outputs'][0]['models'][0]['output']['BMD']
    assert bmd == 29.5318


@pytest.mark.django_db(transaction=False)
def test_c_success(complete_continuous):
    # BMDS execution is slow; we overload this test to check lots of things.
    data = deepcopy(complete_continuous)

    # use a single model for speed
    data['models'] = [
        {'name': 'Linear'},
    ]

    # use alternative BMR definition
    data['bmr'] = {
        'type': 'Std. Dev.',
        'value': 1.5,
    }

    # submit new job
    c = Client()
    payload = json.dumps(data)
    resp = c.post('/api/job/', {'inputs': payload})
    assert resp.status_code == 201

    # poll until job complete
    url = '/api/job/{}/'.format(resp.json()['id'])
    while True:
        time.sleep(2)
        resp = c.get(url)
        if resp.json()['is_finished']:
            break

    # check alternative BMR definition
    outfile = resp.json()['outputs']['outputs'][0]['models'][0]['outfile']
    assert 'Specified effect =           1.5' in outfile

    # check parsed model output exists
    bmd = resp.json()['outputs']['outputs'][0]['models'][0]['output']['BMD']
    assert bmd == 1901.98
