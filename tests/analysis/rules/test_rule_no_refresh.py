from tests.analysis.utils import generate_data

from tornasole.rules import Rule, RequiredTensors
from tornasole.trials import create_trial
import uuid
from tornasole.exceptions import StepNotYetAvailable
from tornasole.analysis.utils import no_refresh


def test_no_refresh_invocation():
  class TestRule(Rule):
    def __init__(self, base_trial):
      super().__init__(base_trial=base_trial)

    def required_tensors(self, step):
      reqt = RequiredTensors(self.base_trial)
      for t in self.base_trial.tensors():
        reqt.need_tensor(t, steps=[step])
      return [reqt]

    def invoke_at_step(self, step):
      for t in self.base_trial.tensors():
        if step == 0:
          assert self.base_trial.tensor(t).value(step + 1) is not None
        elif step == 1:
          try:
            self.base_trial.tensor(t).value(step + 1)
            assert False
          except StepNotYetAvailable:
            pass
  run_id = str(uuid.uuid4())
  base_path = 'ts_output/rule_no_refresh/'
  path = base_path + run_id

  num_tensors = 3

  generate_data(path=base_path, trial=run_id, num_tensors=num_tensors,
                step=0, tname_prefix='foo', worker='algo-1', shape=(3, 3, 3))
  generate_data(path=base_path, trial=run_id, num_tensors=num_tensors,
                step=1, tname_prefix='foo', worker='algo-1', shape=(3, 3, 3))

  tr = create_trial(path)
  r = TestRule(tr)
  r.invoke(0)
  r.invoke(1)

  generate_data(path=base_path, trial=run_id, num_tensors=num_tensors,
                step=2, tname_prefix='foo', worker='algo-1', shape=(3, 3, 3))

  # will not see step2 data
  with no_refresh(tr):
    r.invoke_at_step(1)

  # below will refresh
  try:
    r.invoke(1)
    assert False
  except AssertionError:
    pass