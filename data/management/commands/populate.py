import json
import os

from django.apps import apps
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from data.models import Person, SanctionedEntity


class Command(BaseCommand):
    help = "Populate the database from a JSON file with newline-separated JSON objects"

    def handle(self, *args, **kwargs):
        file_path = "data/raw-data/entities.ftm.json"

        if not os.path.exists(file_path):
            raise CommandError(f"File does not exist: {file_path}")

        try:
            with open(file_path, "r", encoding="utf-8") as file:
                with transaction.atomic():  # Start an atomic transaction
                    for line_number, line in enumerate(file, start=1):
                        try:
                            # Load the JSON object from the line
                            data = json.loads(line.strip())

                            # Extract common fields for SanctionedEntity
                            sanctioned_entity_data = {
                                "id": data.get("id"),
                                "caption": data.get("caption"),
                                "schema": data.get("schema"),
                                "referents": data.get("referents"),
                                "datasets": data.get("datasets"),
                                "first_seen": data.get("first_seen"),
                                "last_seen": data.get("last_seen"),
                                "last_change": data.get("last_change"),
                                "target": data.get("target", False),
                            }

                            # Create or update SanctionedEntity
                            sanctioned_entity, _ = (
                                SanctionedEntity.objects.update_or_create(
                                    id=sanctioned_entity_data["id"],
                                    defaults=sanctioned_entity_data,
                                )
                            )

                            model_path = f"data.{data.get('schema')}"
                            ModelClass = apps.get_model(model_path)
                            model_data = data.get("properties", {})
                            ModelClass.objects.update_or_create(
                                entity=sanctioned_entity,
                                defaults=model_data,
                            )

                        except json.JSONDecodeError:
                            self.stderr.write(
                                f"Invalid JSON on line {line_number}, skipping..."
                            )
                        except Exception as e:
                            self.stderr.write(
                                f"Error processing line {line_number}: {str(e)}"
                            )
                            raise
        except Exception as e:
            raise CommandError(f"An error occurred while processing the file: {str(e)}")

        self.stdout.write(self.style.SUCCESS("Database population complete!"))
