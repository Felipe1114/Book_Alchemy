from symtable import Class

from pydantic import BaseModel, NonNegativeInt, Field
from typing_extensions import Annotated, Optional
from pydantic_extra_types.isbn import ISBN
import annotated_types
from datetime import date as _date

class Author(BaseModel):
	id: NonNegativeInt = Annotated[int, annotated_types.Gt(0)]
	name: str
	birth_date: _date
	date_of_death: Optional[_date] = None

class Book(BaseModel):
	id: NonNegativeInt = Annotated[int, annotated_types.Gt(0)]
	isbn: ISBN
	title: str
	publication_year: Annotated[int, Field(ge=1000, le=_date.today().year)]
	author_id: Annotated[int, annotated_types.Gt(0)]
	

