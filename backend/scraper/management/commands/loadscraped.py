import os
from pathlib import Path

from django.core.management.base import BaseCommand
from quiz.models import Category
from scraper.api_connector import ApiConnector

SCRAPER_DIR = Path(__file__).resolve().parent.parent.parent
DATA_DIR = SCRAPER_DIR / "data"

category_choices = Category.objects.values_list("id", flat=True)
category_choices = list(category_choices)
category_choices.sort()
directory_choices = os.listdir(DATA_DIR)


class Command(BaseCommand):
    help = "Load scraped questions to the database"

    def add_arguments(self, parser):
        parser.add_argument("token", type=str)
        parser.add_argument("directory", type=str, choices=directory_choices)
        parser.add_argument("category", type=int, choices=category_choices)
        parser.add_argument(
            "--verify",
            action="store_true",
            help="Verify all Questions that\
        will be added",
        )

    def handle(self, *args, **options):
        token = options.get("token")
        category = options.get("category")
        directory = options.get("directory")
        verify = options.get("verify")
        print(options)

        path_directory = DATA_DIR / directory
        api = ApiConnector(path_directory, token, category=category)
        api.run()
        self.stdout.write(self.style.SUCCESS("All Questions Loaded Successfully"))

        # work on question verification
        if verify:
            self.stdout.write(
                self.style.SUCCESS(
                    "Setting Verified to be true for all questions loaded."
                )
            )
