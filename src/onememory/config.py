"""OneMemory configuration — paths and settings."""
from pathlib import Path
from pydantic import BaseModel, Field


class Config(BaseModel):
    base_dir: Path = Field(default_factory=lambda: Path.home() / ".onememory")
    proxy_port: int = 8080

    @property
    def hippocampus_dir(self) -> Path:
        return self.base_dir / "hippocampus"

    @property
    def cortex_dir(self) -> Path:
        return self.base_dir / "cortex"

    @property
    def amygdala_dir(self) -> Path:
        return self.base_dir / "amygdala"

    @property
    def dreamlog_dir(self) -> Path:
        return self.base_dir / "dreamlog"

    @property
    def working_memory_dir(self) -> Path:
        return self.base_dir / "working-memory"

    def ensure_dirs(self) -> None:
        for d in [
            self.hippocampus_dir,
            self.cortex_dir,
            self.cortex_dir / "knowledge",
            self.amygdala_dir,
            self.dreamlog_dir,
            self.working_memory_dir,
        ]:
            d.mkdir(parents=True, exist_ok=True)
