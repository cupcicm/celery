from datetime import datetime

import sqlalchemy as sa

from celery import states
from celery.db.session import ResultModelBase
# See docstring of a805d4bd for an explanation for this workaround ;)
if sa.__version__.startswith('0.5'):
    from celery.db.dfd042c7 import PickleType
else:
    from celery.db.a805d4bd import PickleType

try:
  from ltu.utils.jsonutils import FoolProofJsonSerializer
except ImportError, _:
  raise ImportError("You are using a LTU-modified version of celery. "
                    "It needs access to LTU python classes to run.")

class Task(ResultModelBase):
    """Task result/status."""
    __tablename__ = "celery_taskmeta"
    __table_args__ = {"sqlite_autoincrement": True}

    id = sa.Column(sa.Integer, sa.Sequence("task_id_sequence"),
                   primary_key=True,
                   autoincrement=True)
    task_id = sa.Column(sa.String(255), unique=True)
    status = sa.Column(sa.String(50), default=states.PENDING)
    result = sa.Column(PickleType(pickler=FoolProofJsonSerializer()), nullable=True)
    date_done = sa.Column(sa.DateTime, default=datetime.now,
                       onupdate=datetime.now, nullable=True)
    traceback = sa.Column(sa.Text, nullable=True)

    def __init__(self, task_id):
        self.task_id = task_id

    def to_dict(self):
        return {"task_id": self.task_id,
                "status": self.status,
                "result": self.result,
                "traceback": self.traceback,
                "date_done": self.date_done}

    def __eq__(self, other):
        return self.task_id == other.task_id

    def __repr__(self):
        return "<Task %s state: %s>" % (self.task_id, self.status)


class TaskSet(ResultModelBase):
    """TaskSet result"""
    __tablename__ = "celery_tasksetmeta"
    __table_args__ = {"sqlite_autoincrement": True}

    id = sa.Column(sa.Integer, sa.Sequence("taskset_id_sequence"),
                autoincrement=True, primary_key=True)
    taskset_id = sa.Column(sa.String(255), unique=True)
    result = sa.Column(sa.PickleType(pickler=FoolProofJsonSerializer()), nullable=True)
    date_done = sa.Column(sa.DateTime, default=datetime.now,
                       nullable=True)

    def __init__(self, taskset_id, result):
        self.taskset_id = taskset_id
        self.result = result

    def to_dict(self):
        return {"taskset_id": self.taskset_id,
                "result": self.result,
                "date_done": self.date_done}

    def __repr__(self):
        return u"<TaskSet: %s>" % (self.taskset_id, )
