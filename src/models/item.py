"""
src/models/item.py

Using Pydantic for data validation and modeling.
When we scrape data, it's often unstructured (just strings).
Pydantic ensures our data is strictly shaped and validated
before we store or process it further.
"""

from typing import Optional
from pydantic import BaseModel, Field, HttpUrl, field_validator


class BookItem(BaseModel):
    """
    Data model representing a book.
    Ensures all extracted fields are present and valid.
    """

    title: str
    price: str
    rating: str
    availability: str
    url: HttpUrl

    # Detail fields (Optional since they're only filled after detail scraping)
    description: Optional[str] = None
    upc: Optional[str] = None
    product_type: Optional[str] = None
    price_excl_tax: Optional[str] = None
    price_incl_tax: Optional[str] = None
    tax: Optional[str] = None
    availability_stock: Optional[str] = None
    num_reviews: Optional[int] = 0

    @field_validator("num_reviews", mode="before")
    def parse_reviews(cls, v):
        """
        Custom validator to handle raw string to int conversion
        for the number of reviews.
        """
        if isinstance(v, str):
            # If the site gives us "0", we convert to int(0)
            try:
                return int(v)
            except ValueError:
                return 0
        return v
