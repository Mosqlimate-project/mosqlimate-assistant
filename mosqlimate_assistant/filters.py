from typing import Optional, Literal
from pydantic import BaseModel, Field, constr

class InfodengueFilters(BaseModel):
    disease: Literal['dengue', 'zika', 'chik', 'chikungunya'] = Field(
        ..., description="Doença: 'dengue', 'zika', 'chik' ou 'chikungunya'"
    )
    start: constr(pattern=r'^\d{4}-\d{2}-\d{2}$') = Field(..., description="Data de início (YYYY-mm-dd)")
    end: constr(pattern=r'^\d{4}-\d{2}-\d{2}$') = Field(..., description="Data de término (YYYY-mm-dd)")
    uf: Optional[Literal["AC", "AL", "AP", "AM", "BA", "CE", "DF", "ES", "GO", "MA", "MT", "MS", "MG", "PA", "PB", "PR", "PE", "PI", "RJ", "RN", "RS", "RO", "RR", "SC", "SP", "SE", "TO"]] = Field(
        None, description="Sigla do estado brasileiro (duas letras), ex: SP"
    )
    geocode: Optional[int] = Field(
        None, description="Código do município segundo o IBGE"
    )

    class Config:
        extra = "ignore"

class ClimateFilters(BaseModel):
    start: constr(pattern=r'^\d{4}-\d{2}-\d{2}$') = Field(..., description="Data de início (YYYY-mm-dd)")
    end: constr(pattern=r'^\d{4}-\d{2}-\d{2}$') = Field(..., description="Data de término (YYYY-mm-dd)")
    uf: Optional[Literal["AC", "AL", "AP", "AM", "BA", "CE", "DF", "ES", "GO", "MA", "MT", "MS", "MG", "PA", "PB", "PR", "PE", "PI", "RJ", "RN", "RS", "RO", "RR", "SC", "SP", "SE", "TO"]] = Field(
        None, description="Sigla do estado brasileiro (duas letras), ex: SP"
    )
    geocode: Optional[int] = Field(
        None, description="Código do município segundo o IBGE"
    )

    class Config:
        extra = "ignore"

class MosquitoFilters(BaseModel):
    key: str = Field(..., description="ContaOvos API key")

    class Config:
        extra = "ignore"

class EpiscannerFilters(BaseModel):
    disease: Literal['dengue', 'zika', 'chik', 'chikungunya'] = Field(
        ..., description="Doença: 'dengue', 'zika', 'chik' ou 'chikungunya'"
    )
    uf: Literal["AC", "AL", "AP", "AM", "BA", "CE", "DF", "ES", "GO", "MA", "MT", "MS", "MG", "PA", "PB", "PR", "PE", "PI", "RJ", "RN", "RS", "RO", "RR", "SC", "SP", "SE", "TO"] = Field(
        ..., description="Sigla do estado brasileiro (duas letras), ex: SP"
    )
    year: Optional[int] = Field(None, description="Ano específico")

    class Config:
        extra = "ignore"

