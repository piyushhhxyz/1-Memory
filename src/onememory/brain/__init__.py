from onememory.brain.hippocampus import Hippocampus
from onememory.brain.cortex import Cortex
from onememory.brain.amygdala import Amygdala
from onememory.brain.prefrontal import PrefrontalCortex
from onememory.config import Config


def create_brain(config: Config | None = None) -> PrefrontalCortex:
    config = config or Config()
    config.ensure_dirs()
    hippocampus = Hippocampus(config)
    amygdala = Amygdala(config)
    cortex = Cortex(config)
    return PrefrontalCortex(config, hippocampus, cortex, amygdala)
