import logging
from threadlocals.threadlocals import get_thread_variable
from users.models import Record

business_logger = logging.getLogger('business')


def get_current_user():
    return get_thread_variable('thread_user')


def create_record(user, action, model, detail, instance_id):
    if user is None:
        return
    try:
        Record.objects.create(user=user, action=action, model=model, detail=detail, instance_id=instance_id)
    except Exception as e:
        business_logger.error(f"[{model}] Audit record failed: {e}")
