"""Brain module — Factory wiring for all memory components."""
from onememory.brain.hippocampus import Hippocampus
from onememory.brain.cortex import Cortex
from onememory.brain.amygdala import Amygdala
from onememory.brain.prefrontal import PrefrontalCortex
from onememory.config import Config


def create_brain(config: Config | None = None) -> PrefrontalCortex:
    """Factory function — wires up hippocampus, cortex, amygdala, and prefrontal cortex."""
    config = config or Config()
    config.ensure_dirs()
    hippocampus = Hippocampus(config)
    amygdala = Amygdala(config)
    cortex = Cortex(config)
    return PrefrontalCortex(config, hippocampus, cortex, amygdala)
