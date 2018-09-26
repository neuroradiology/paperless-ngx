import logging

from django.core.management.base import BaseCommand

from documents.classifier import DocumentClassifier
from documents.models import Document, Tag

from ...mixins import Renderable


class Command(Renderable, BaseCommand):

    help = """
        Using the current classification model, assigns correspondents, tags
        and document types to all documents, effectively allowing you to
        back-tag all previously indexed documents with metadata created (or
        modified) after their initial import.
    """.replace("    ", "")

    def __init__(self, *args, **kwargs):
        self.verbosity = 0
        BaseCommand.__init__(self, *args, **kwargs)

    def add_arguments(self, parser):
        parser.add_argument(
            "-c", "--correspondent",
            action="store_true"
        )
        parser.add_argument(
            "-T", "--tags",
            action="store_true"
        )
        parser.add_argument(
            "-t", "--type",
            action="store_true"
        )
        parser.add_argument(
            "-i", "--inbox-only",
            action="store_true"
        )
        parser.add_argument(
            "-r", "--replace-tags",
            action="store_true"
        )

    def handle(self, *args, **options):

        self.verbosity = options["verbosity"]

        if options["inbox_only"]:
            queryset = Document.objects.filter(tags__is_inbox_tag=True)
        else:
            queryset = Document.objects.all()
        documents = queryset.distinct()

        logging.getLogger(__name__).info("Loading classifier")
        clf = DocumentClassifier()
        try:
            clf.reload()
        except FileNotFoundError:
            logging.getLogger(__name__).fatal("Cannot classify documents, "
                                              "classifier model file was not "
                                              "found.")
            return

        for document in documents:
            logging.getLogger(__name__).info(
                "Processing document {}".format(document.title)
            )
            clf.classify_document(
                document,
                classify_document_type=options["type"],
                classify_tags=options["tags"],
                classify_correspondent=options["correspondent"],
                replace_tags=options["replace_tags"]
            )
