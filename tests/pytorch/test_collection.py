from tornasole.pytorch.hook import TornasoleHook as t_hook
from tornasole.pytorch import SaveConfig, Collection, ReductionConfig, reset_collections
import tornasole.pytorch as ts
from tornasole.trials import create_trial
import shutil
import torch
import torch.optim as optim
from datetime import datetime
import os
from .utils import Net, train


def test_collection_add(hook=None, out_dir=None):
    hook_created = False
    if hook is None:
        reset_collections()
        run_id = "trial_" + datetime.now().strftime("%Y%m%d-%H%M%S%f")
        out_dir = "./newlogsRunTest/" + run_id
        hook = t_hook(
            out_dir=out_dir,
            save_config=SaveConfig(save_steps=[0, 1, 2, 3]),
            include_collections=["relu_activations"],
        )
        hook_created = True

    model = Net().to(torch.device("cpu"))
    hook.register_hook(model)
    optimizer = optim.SGD(model.parameters(), lr=0.001, momentum=0.9)
    train(model, hook, torch.device("cpu"), optimizer, num_steps=10)
    tr = create_trial(out_dir)
    assert tr
    assert len(tr.tensors_in_collection("relu_activations")) > 0
    assert tr.tensor(tr.tensors_in_collection("relu_activations")[0]).value(0) is not None

    if hook_created:
        shutil.rmtree(out_dir)