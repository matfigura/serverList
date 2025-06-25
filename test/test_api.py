import pytest
from flaskr import create_app
from flaskr.db import db
from flaskr.models.user import User

@pytest.fixture
def app():
    app = create_app('testing')
    app.config.update({
        'TESTING': True,
        'SQLALCHEMY_DATABASE_URI': 'sqlite:///:memory:',
        'SQLALCHEMY_TRACK_MODIFICATIONS': False
    })
    with app.app_context():
        # 1) Utworzenie schematu w in-memory SQLite
        db.create_all()

        # 2) Dodanie jednego testowego użytkownika z wymaganymi polami
        user = User(
            username='testuser',
            email='test@example.com',
            password='testpass'
        )
        db.session.add(user)
        db.session.commit()

        # 3) Przechowujemy w app.test_user dla łatwego dostępu
        app.test_user = user

        yield app

        # 4) Sprzątanie po teście
        db.drop_all()

@pytest.fixture
def client(app):
    return app.test_client()

def test_servers_crud(client, app):
    user_id = app.test_user.id

    # CREATE
    resp = client.post('/servers/', json={
        'name': 'Srv1',
        'ip': '1.2.3.4',
        'description': 'Desc',
        'user_id': user_id
    })
    assert resp.status_code == 201
    srv_id = resp.get_json()['id']

    # READ all
    resp = client.get('/servers/')
    assert resp.status_code == 200
    assert any(s['id'] == srv_id for s in resp.get_json())

    # READ one
    resp = client.get(f'/servers/{srv_id}')
    assert resp.status_code == 200
    data = resp.get_json()
    assert data['name'] == 'Srv1'
    assert data['user_id'] == user_id

    # UPDATE
    resp = client.put(f'/servers/{srv_id}', json={
        'name': 'SrvX',
        'ip_address': '9.9.9.9',
        'user_id': user_id
    })
    assert resp.status_code == 200
    updated = client.get(f'/servers/{srv_id}').get_json()
    assert updated['name'] == 'SrvX'
    assert updated['ip_address'] == '9.9.9.9'

    # DELETE
    resp = client.delete(f'/servers/{srv_id}')
    assert resp.status_code == 200
    assert client.get(f'/servers/{srv_id}').status_code == 404

def test_skins_crud(client, app):
    user_id = app.test_user.id

    # najpierw trzeba mieć serwer
    resp_srv = client.post('/servers/', json={
        'name': 'SrvSkin',
        'ip': '5.5.5.5',
        'description': 'D',
        'user_id': user_id
    })
    srv_id = resp_srv.get_json()['id']

    # CREATE
    resp = client.post('/skins/', json={
        'server_id': srv_id,
        'name': 'Skin1',
        'image_url': 'url1'
    })
    assert resp.status_code == 201
    skin_id = resp.get_json()['id']

    # READ all
    resp = client.get('/skins/')
    assert resp.status_code == 200
    assert any(s['id'] == skin_id for s in resp.get_json())

    # READ one
    resp = client.get(f'/skins/{skin_id}')
    assert resp.status_code == 200
    assert resp.get_json()['name'] == 'Skin1'

    # UPDATE
    resp = client.put(f'/skins/{skin_id}', json={'name': 'SkinX'})
    assert resp.status_code == 200
    assert client.get(f'/skins/{skin_id}').get_json()['name'] == 'SkinX'

    # DELETE
    resp = client.delete(f'/skins/{skin_id}')
    assert resp.status_code == 200
    assert client.get(f'/skins/{skin_id}').status_code == 404

def test_votes_crud_and_rate_limit(client, app):
    # musimy mieć serwer
    resp_srv = client.post('/servers/', json={
        'name': 'SrvVote',
        'ip': '7.7.7.7',
        'description': '',
        'user_id': app.test_user.id
    })
    srv_id = resp_srv.get_json()['id']

    # pierwszy głos – OK
    resp = client.post('/votes/', json={
        'server_id': srv_id,
        'ip_address': '9.9.9.9'
    })
    assert resp.status_code == 201
    vote_id = resp.get_json()['id']

    # drugi z tego samego IP w ciągu 24h – 403
    resp2 = client.post('/votes/', json={
        'server_id': srv_id,
        'ip_address': '9.9.9.9'
    })
    assert resp2.status_code == 403

    # READ votes
    resp = client.get('/votes/')
    assert resp.status_code == 200
    assert any(v['id'] == vote_id for v in resp.get_json())