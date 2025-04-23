# mosqlimate-assistant
AI assistant to explai the platform

---
On mosqlimate api documentation, we have the following [description](https://api.mosqlimate.org/docs/datastore/GET/infodengue/) about the datastore:


---

## Infodengue:

| Parameter name | Required | Type                | Description |
|---------------|----------|---------------------|-------------|
| *page        | yes      | int                 | Page to be displayed |
| *per_page    | yes      | int                 | How many items will be displayed per page (up to 100) |
| disease      | yes      | str                 | Dengue, Zika or Chik[ungunya] |
| start        | yes      | str *(YYYY-mm-dd)*  | Start date (epidemiological week) |
| end          | yes      | str *(YYYY-mm-dd)*  | End date (epidemiological week) |
| uf           | no       | str *(UF)*          | Two letters Brazilian state abbreviation. E.g: SP |
| geocode      | no       | int                 | [IBGE's](https://www.ibge.gov.br/explica/codigos-dos-municipios.php) municipality code |

---

## Climate

| Parameter name | Required | Type               | Description |
|---------------|----------|--------------------|-------------|
| *page        | yes      | int                | Page to be displayed |
| *per_page    | yes      | int                | How many items will be displayed per page (up to 100) |
| start        | yes      | str *(YYYY-mm-dd)* | Start date |
| end          | yes      | str *(YYYY-mm-dd)* | End date |
| geocode      | no       | int                | [IBGE's](https://www.ibge.gov.br/explica/codigos-dos-municipios.php) municipality code |
| uf           | no       | str *(UF)*         | Two-letter Brazilian state abbreviation. E.g.: SP |

---

## Mosquito

| Parameter name | Required | Type | Description           |
|---------------|----------|------|-----------------------|
| key          | yes      | str  | ContaOvos API key    |
| page         | yes      | int  | Page to be displayed |

---

## Episcanner

| Parameter name | Required | Type       | Description |
|---------------|----------|------------|-------------|
| disease      | yes      | str        | Specific disease. Options: dengue, zika, chik |
| uf          | yes      | str *(UF)* | Two-letter Brazilian state abbreviation. E.g.: SP |
| year        | no       | int        | Specific year. Default: current year |
