from pathlib import Path
from pydantic import BaseModel, Field


class Config(BaseModel):
    base_dir: Path = Field(default_factory=lambda: Path.home() / ".onememory")
    proxy_port: int = 11411
    openai_base_url: str = "https://api.openai.com"
    anthropic_base_url: str = "https://api.anthropic.com"

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

    @property
    def config_file(self) -> Path:
        return self.base_dir / "config.json"

    def ensure_dirs(self) -> None:
        for d in [
            self.hippocampus_dir,
            self.cortex_dir,
            self.cortex_dir / "knowledge",
            self.amygdala_dir,
            self.dreamlog_dir,
            self.working_memory_dir,
            self.base_dir / "procedural",
        ]:
            d.mkdir(parents=True, exist_ok=True)
