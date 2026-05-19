from pydantic import ValidationError as PydanticValidationError
from rest_framework.exceptions import ValidationError


def pydantic_to_drf_error(error: PydanticValidationError):
    detail = {}
    for item in error.errors():
        field = item["loc"][0] if item["loc"] else "non_field_errors"
        detail.setdefault(field, []).append(item["msg"])
    raise ValidationError(detail)


def build_schema(schema_class, data):
    try:
        return schema_class(**data)
    except PydanticValidationError as error:
        pydantic_to_drf_error(error)
