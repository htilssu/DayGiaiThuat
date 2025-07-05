def model_to_dict(instance):
    return {c.name: getattr(instance, c.name) for c in instance.__table__.columns}
