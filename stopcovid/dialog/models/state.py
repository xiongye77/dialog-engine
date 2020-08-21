import uuid
import datetime
from typing import Optional

import pydantic

from stopcovid.dialog.models import SCHEMA_VERSION
from stopcovid.dialog.registration import AccountInfo
from stopcovid.drills import drills


class UserProfile(pydantic.BaseModel):
    validated: bool
    opted_out: bool = False
    is_demo: bool = False
    language: Optional[str] = None
    account_info: Optional[AccountInfo] = None

    @pydantic.validator("language", pre=True, always=True)
    def set_language(cls, value):
        if value is not None:
            return value.lower()[:2]


class PromptState(pydantic.BaseModel):
    slug: str
    start_time: datetime.datetime
    failures: Optional[int] = 0
    reminder_triggered: Optional[bool] = False
    last_response_time: Optional[datetime.datetime] = None


class DialogState(pydantic.BaseModel):
    phone_number: str
    seq: str
    user_profile: Optional[UserProfile] = pydantic.Field(
        default_factory=lambda: UserProfile(validated=False)
    )
    current_drill: Optional[drills.Drill] = None
    drill_instance_id: Optional[uuid.UUID] = None
    current_prompt_state: Optional[PromptState] = None
    schema_version: int = SCHEMA_VERSION

    def get_prompt(self) -> Optional[drills.Prompt]:
        if self.current_drill is None or self.current_prompt_state is None:
            return None
        return self.current_drill.get_prompt(self.current_prompt_state.slug)

    def get_next_prompt(self) -> Optional[drills.Prompt]:
        return self.current_drill.get_next_prompt(self.current_prompt_state.slug)

    def is_next_prompt_last(self) -> bool:
        return self.current_drill.prompts[-1].slug == self.get_next_prompt().slug
