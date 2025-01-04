from pydantic import BaseModel, Field

# class InformationToWalk(BaseModel):
#     title: str = Field(..., description="Title of the information")
#     link: str = Field(..., description="Link of the information")


class ImportantInformation(BaseModel):
    title: str #= Field(..., description="Title of important information (postech students must know this)")
    links: str #= Field(..., description="Links of information (postech students must know this)")