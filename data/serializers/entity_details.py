from django.db import models
from rest_framework import status
from rest_framework.exceptions import NotFound
from rest_framework.response import Response
from rest_framework.views import APIView

from ..models import SanctionedEntity


class EntityDetailSerializer:
    """
    Custom serializer to dynamically structure the response for SanctionedEntity
    and all its related models dynamically.
    """
    def __init__(self, entity):
        self.entity = entity

    def serialize_field(self, value):
        """
        Convert a field value to a JSON-serializable format.
        """
        if isinstance(value, models.Model):
            # If the field is a related model, return its string representation
            return str(value)
        elif isinstance(value, (list, dict)):
            # Return the value directly if it is already JSON-serializable
            return value
        elif hasattr(value, "__dict__"):
            # For objects with attributes, serialize their dictionary representation
            return {k: v for k, v in value.__dict__.items() if not k.startswith("_")}
        else:
            # For other types (e.g., numbers, strings), return the value as is
            return value

    def to_dict(self):
        data = {
            "id": self.entity.sanctionId,
            "name": self.entity.caption,
            "attributes": {
                "schema": self.serialize_field(self.entity.schema),
                "datasets": self.serialize_field(self.entity.datasets),
                "first_seen": self.serialize_field(self.entity.first_seen),
                "last_seen": self.serialize_field(self.entity.last_seen),
                "last_change": self.serialize_field(self.entity.last_change),
                "target": self.serialize_field(self.entity.target),
            },
            "linkedEntities": []
        }

        # Dynamically include all related one-to-one models
        related_objects = self.entity._meta.related_objects
        for related in related_objects:
            if related.one_to_one:  # Only handle one-to-one relationships
                related_name = related.get_accessor_name()
                try:
                    related_instance = getattr(self.entity, related_name)
                    related_data = {
                        field.name: self.serialize_field(getattr(related_instance, field.name))
                        for field in related_instance._meta.fields
                    }
                    related_data["id"] = related_instance.id  # Explicitly include ID
                    related_data["type"] = related_name.capitalize()
                    data["linkedEntities"].append(related_data)
                except related.related_model.DoesNotExist:
                    pass

        return data