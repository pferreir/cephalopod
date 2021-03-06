import uuid
from datetime import datetime

from flask import jsonify, request
from sqlalchemy.exc import SQLAlchemyError

from ..core import db
from ..models import Instance
from . import bp


@bp.route('/instance/', methods=('POST',))
def create_instance():
    payload = request.get_json()
    print payload
    instance = Instance()
    instance.uuid = str(uuid.uuid4())
    instance.url = payload['url'].rstrip('/')
    instance.contact = payload['contact']
    instance.email = payload['email']
    instance.organisation = payload['organisation']
    instance.registration_date = datetime.utcnow()
    db.session.add(instance)
    db.session.commit()
    return jsonify(uuid=instance.uuid)


@bp.route('/instance/<uuid>', methods=('PATCH',))
def update_instance(uuid):
    instance = Instance.query.filter_by(uuid=uuid).first_or_404()
    fields = ['enabled', 'url', 'contact', 'email', 'organisation']
    payload = request.get_json()
    for field in fields:
        value = payload.pop(field, None)
        if value is None:
            continue
        if value == '':
            return jsonify(error='Invalid value', field=field), 400
        if field == 'url':
            value = value.rstrip('/')
        setattr(instance, field, value)
    if payload:
        return jsonify(error='Unexpected data', data=payload), 400
    try:
        db.session.commit()
    except SQLAlchemyError as e:
        db.session.rollback()
        return jsonify(error=str(e)), 400
    return jsonify(**instance.__json__())


@bp.route('/instance/<uuid>')
def get_instance(uuid):
    instance = Instance.query.filter_by(uuid=uuid).first()
    if instance is None:
        rv = jsonify()
        rv.status_code = 404
    else:
        rv = jsonify(**instance.__json__())
    rv.headers['Access-Control-Allow-Origin'] = '*'
    return rv
