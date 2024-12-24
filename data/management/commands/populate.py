import json
import os

from django.apps import apps
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from data.models import SanctionedEntity

from ...script.download import DataDownloader


class Command(BaseCommand):
    help = "Populate the database from a JSON file with newline-separated JSON objects"

    def handle(self, *args, **kwargs):
        self.stdout.write("Pulling latest data from the source")

        BASE_URL = "https://www.opensanctions.org/datasets/sanctions/"
        DOWNLOAD_DIR = "data/raw-data/"

        os.makedirs(DOWNLOAD_DIR, exist_ok=True)

        # DataDownloader instance and download the file
        downloader = DataDownloader(BASE_URL, DOWNLOAD_DIR)
        downloader.download_data("entities.ftm.json")
        downloader.download_data("names.txt")
        downloader.download_data("senzing.json")
        downloader.download_data("targets.nested.json")
        downloader.download_data("targets.simple.csv")
        self.stdout.write("Download Complete")

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
                            self.stdout.write(f"On line no: {line_number}")

                            # Extract common fields for SanctionedEntity
                            sanctioned_entity_data = {
                                "sanctionId": data.get("id"),
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
                                    sanctionId=sanctioned_entity_data["sanctionId"],
                                    defaults=sanctioned_entity_data,
                                )
                            )

                            model_path = f"data.{data.get('schema')}"
                            ModelClass = apps.get_model(model_path)
                            model_data = data.get("properties", {})
                            ModelClass.objects.update_or_create(
                                sanctionEntity=sanctioned_entity,
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
