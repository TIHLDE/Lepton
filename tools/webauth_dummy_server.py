#!/bin/env python3

# Dummy WebAuth server for testing purposes.
# Modified from github.com/tihlde/WebAuth

from aiohttp import web
import aiohttp_cors
import secrets
import json

from logzero import logger

app = web.Application()

# Use the following credentials for
# logging in with this dummy
users = {
    'username': {
        'password': 'test12345',
    },
    'admin': {
        'password': 'adminpassword',
    },
    'abcdef': {
        'password': 'test'
    },
    'super': {
        'password': 'super'
    }
}

sessions = {}

def create_session(username):
    token = secrets.token_hex(64)
    logger.info('Created session for user {}'.format(username))
    sessions[token] = {
        "memberof_group": [
            "list",
        ],
        "cn": [
            "Full Name"
        ],
        "homedirectory": [
            "/path/to/home/directory"
        ],
        "uid": [username],
        "mail": [
            "list.of@emails"
        ],
        "givenname": [
            "Firstname"
        ],
        "sn": [
            "Lastname"
        ]
    }
    return token

async def auth(request):
    body = await request.json()
    if 'username' in body or 'password' in body:
        username, password = body['username'], body['password']
        logger.info('Recieved auth username: {}, password: {}'.format(username, password))
        if username in users:
            user = users[username]
            if user['password'] == password:
                token = create_session(username)
                return web.Response(status=200,
                            body=json.dumps({'token': token}),
                            content_type='application/json')

    return web.Response(status=401,
                        body=json.dumps({'msg': 'invalid credentials'}),
                        content_type='application/json')

async def logout(request):
    token = request.headers.get('X-CSRF-Token')
    logger.info('Recieved logout: token: {}'.format(token))

    if token in sessions:
        session = sessions.pop(token)
        return web.Response(status=200, body=json.dumps(session),
                            content_type='application/json')

    return web.Response(status=205, body=json.dumps(
                            {'msg': 'no session exists by that token'}),
                        content_type='application/json')

async def setpw(request):
    token = request.headers.get('X-CSRF-Token')
    session = sessions.get(token, None)
    body = await request.json()
    logger.info('Recieved setpw: token: {}, body: {}'.format(token, body))
    if not session:
        return web.Response(
            status=401,
            body=json.dumps({'msg': 'invalid token'}),
            content_type='application/json')

    if not 'new-password' in body or not 'old-password' in body:
        return web.Response(
            status=401,
            body=json.dumps({'msg': 'invalid request'}),
            content_type='application/json')

    username = session['uid'][0]
    user = users[username]
    if user['password'] != body['old-password']:
        return web.Response(
            status=401,
            body=json.dumps({'msg': 'old password is invalid'}),
            content_type='application/json')

    user['password'] = body['new-password']
    users[username] = user

    sessions.pop(token, None)
    token = create_session(username)

    return web.Response(
        status=200,
        body=json.dumps({'msg': 'Password has been reset', 'token': token}),
        content_type='application/json')

async def verify(request):
    token = request.headers.get('X-CSRF-Token')
    logger.info('Recieved verify: token: {}'.format(token))
    if token in sessions:
        session = sessions[token]
        return web.Response(
            status=200,
            body=json.dumps(session),
            content_type='application/json'
        )

    return web.Response(
        status=402,
        body=json.dumps({'msg': 'invalid token'}),
        content_type='application/json'
    )

cors = aiohttp_cors.setup(app, defaults={
    "*": aiohttp_cors.ResourceOptions(
        allow_credentials=True,
        expose_headers="*",
        allow_headers="*",)
})

cors = aiohttp_cors.setup(app, defaults={
    "*": aiohttp_cors.ResourceOptions(
        allow_credentials=True,
        expose_headers="*",
        allow_headers="*",)
})

app.router.add_post('/api/v1/auth', auth)
app.router.add_post('/api/v1/logout', logout)
app.router.add_post('/api/v1/setpw', setpw)
app.router.add_get('/api/v1/verify', verify)

for route in list(app.router.routes()):
    cors.add(route)

from os import environ
port = environ.get('PORT', 3444)


web.run_app(app, host='0.0.0.0', port=port)
