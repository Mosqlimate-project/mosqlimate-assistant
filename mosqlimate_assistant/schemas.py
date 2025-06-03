import re
from typing import Literal, Optional

import epiweeks
from pydantic import BaseModel, ConfigDict, Field, field_validator

from mosqlimate_assistant.settings import Diseases, UFs


def _last_epiweek():
    return epiweeks.Week.thisweek() - 1


def _default_start():
    return _last_epiweek().startdate().isoformat()


def _default_end():
    return _last_epiweek().enddate().isoformat()


class TableFilters(BaseModel):
    table: Literal["infodengue", "climate", "mosquito", "episcanner"] = Field(
        default=...,
        description="Tabela a ser consultada: 'infodengue', 'climate', 'mosquito' ou 'episcanner'",
    )
    disease: Optional[Diseases] = Field(
        default=None,
        description="Doença: 'dengue', 'zika' ou 'chikungunya'",
    )
    start: str = Field(
        default_factory=_default_start,
        description="Data de início (YYYY-mm-dd)",
    )
    end: str = Field(
        default_factory=_default_end,
        description="Data de término (YYYY-mm-dd)",
    )
    uf: Optional[UFs] = Field(
        default=None,
        description="Sigla do estado brasileiro (duas letras), ex: SP",
    )
    city: Optional[str] = Field(default=None, description="Nome do município")
    key: Optional[str] = Field(default=None, description="ContaOvos API key")
    year: Optional[int] = Field(default=None, description="Ano específico")

    @field_validator("start", mode="before")
    def _validate_start(cls, v):
        if isinstance(v, str) and re.match(r"^\d{4}-\d{2}-\d{2}$", v):
            return v
        return _default_start()

    @field_validator("end", mode="before")
    def _validate_end(cls, v):
        if isinstance(v, str) and re.match(r"^\d{4}-\d{2}-\d{2}$", v):
            return v
        return _default_end()

    model_config = ConfigDict(extra="ignore")


class InfodengueFilters(BaseModel):
    table: Literal["infodengue"] = Field(default="infodengue")
    disease: Literal[Diseases] = Field(
        default=..., description="Doença: 'dengue', 'zika' ou 'chikungunya'"
    )
    start: str = Field(
        default=...,
        pattern=r"^\d{4}-\d{2}-\d{2}$",
        description="Data de início (YYYY-mm-dd)",
    )
    end: str = Field(
        default=...,
        pattern=r"^\d{4}-\d{2}-\d{2}$",
        description="Data de término (YYYY-mm-dd)",
    )
    uf: Optional[UFs] = Field(
        default=None,
        description="Sigla do estado brasileiro (duas letras), ex: SP",
    )
    city: Optional[str] = Field(default=None, description="Nome do município")

    model_config = ConfigDict(extra="ignore")


class ClimateFilters(BaseModel):
    table: Literal["climate"] = Field(default="climate")
    start: str = Field(
        default=...,
        pattern=r"^\d{4}-\d{2}-\d{2}$",
        description="Data de início (YYYY-mm-dd)",
    )
    end: str = Field(
        default=...,
        pattern=r"^\d{4}-\d{2}-\d{2}$",
        description="Data de término (YYYY-mm-dd)",
    )
    uf: Optional[UFs] = Field(
        default=None,
        description="Sigla do estado brasileiro (duas letras), ex: SP",
    )
    city: Optional[str] = Field(default=None, description="Nome do município")

    model_config = ConfigDict(extra="ignore")


class MosquitoFilters(BaseModel):
    table: Literal["mosquito"] = Field(default="mosquito")
    key: str = Field(default=..., description="ContaOvos API key")

    model_config = ConfigDict(extra="ignore")


class EpiscannerFilters(BaseModel):
    table: Literal["episcanner"] = Field(default="episcanner")
    disease: Literal[Diseases] = Field(
        default=...,
        description="Doença: 'dengue', 'zika' ou 'chikungunya'",
    )
    uf: UFs = Field(
        default=...,
        description="Sigla do estado brasileiro (duas letras), ex: SP",
    )
    year: Optional[int] = Field(default=None, description="Ano específico")

    model_config = ConfigDict(extra="ignore")
