from typing import Literal, Optional

from pydantic import BaseModel, ConfigDict, Field

Diseases = Literal[
    "dengue",
    "zika",
    "chik",
    "chikungunya",
]

UFs = Literal[
    "AC",
    "AL",
    "AP",
    "AM",
    "BA",
    "CE",
    "DF",
    "ES",
    "GO",
    "MA",
    "MT",
    "MS",
    "MG",
    "PA",
    "PB",
    "PR",
    "PE",
    "PI",
    "RJ",
    "RN",
    "RS",
    "RO",
    "RR",
    "SC",
    "SP",
    "SE",
    "TO",
]


class TableFilters(BaseModel):
    table: Literal["infodengue", "climate", "mosquito", "episcanner"] = Field(
        default=...,
        description="Tabela a ser consultada: 'infodengue', 'climate', 'mosquito' ou 'episcanner'",
    )
    disease: Optional[Diseases] = Field(
        default=None,
        description="Doença: 'dengue', 'zika' ou 'chikungunya'",
    )
    start: Optional[str] = Field(
        default=None,
        pattern=r"^\d{4}-\d{2}-\d{2}$",
        description="Data de início (YYYY-mm-dd)",
    )
    end: Optional[str] = Field(
        default=None,
        pattern=r"^\d{4}-\d{2}-\d{2}$",
        description="Data de término (YYYY-mm-dd)",
    )
    uf: Optional[UFs] = Field(
        default=None,
        description="Sigla do estado brasileiro (duas letras), ex: SP",
    )
    city: Optional[str] = Field(default=None, description="Nome do município")
    key: Optional[str] = Field(default=None, description="ContaOvos API key")
    year: Optional[int] = Field(default=None, description="Ano específico")

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
        description="Doença: 'dengue', 'zika', 'chik' ou 'chikungunya'",
    )
    uf: UFs = Field(
        default=...,
        description="Sigla do estado brasileiro (duas letras), ex: SP",
    )
    year: Optional[int] = Field(default=None, description="Ano específico")

    model_config = ConfigDict(extra="ignore")
