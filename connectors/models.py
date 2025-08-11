from django.db import models
from django.conf import settings
from polymorphic.models import PolymorphicModel
from connectors.utils import scrape_page, scrape_listing_page
import random


class Connector(PolymorphicModel):
    name = models.CharField(max_length=255, default="")

    def __str__(self):
        return getattr(self.name, "name", f"Connector {self.pk}")


class ManualConnector(Connector):
    content_data = models.TextField()

    def __str__(self):
        return f"Manual Connector:  {self.name}"

    @property
    def get_content_data(self):
        return self.content_data

    @property
    def get_image_urls(self):
        return [f"{settings.DOMAIN}{image.image.url}" for image in self.images.all()]


class ManualConnectorImage(models.Model):
    manual_connector = models.ForeignKey(
        ManualConnector, related_name="images", on_delete=models.CASCADE
    )
    image = models.ImageField(upload_to="media_content_images/")

    def __str__(self):
        return f"Image for Media Content {self.manual_connector.pk}"


class ScraperConnector(Connector):
    base_url = models.URLField(help_text="Main page to scrape from")

    image_selector = models.CharField(
        max_length=255, help_text="CSS selector for the image element"
    )
    title_selector = models.CharField(
        max_length=255, help_text="CSS selector for the title element"
    )
    description_selector = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        help_text="Optional CSS selector for description",
    )

    last_ran = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Scraper Connector: {self.name}"

    def persist_scraped_data(self, scraped_data):
        for data in scraped_data:
            ScrappedItem.objects.create(connector=self, scraped_data=data)

    def get_scraped_data(self, for_social_media=None, for_channel=None):
        posted_items_pks = SocialPost.objects.filter(
            scrapped_item__connector=self,
            social_media=for_social_media,
            content_type=for_channel,
        ).values_list("scrapped_item__pk", flat=True)

        if self.scrapped_items.exists():
            items = list(self.scrapped_items.all().exclude(pk__in=posted_items_pks))
            if items:
                return random.choice(items).scraped_data
            return None
        else:
            scraped_data = scrape_listing_page(
                self.base_url,
                self.image_selector,
                self.title_selector,
                self.description_selector,
            )
            self.persist_scraped_data(scraped_data)
            return scraped_data

    def get_content_data(self, for_social_media=None, for_channel=None):
        scraped_data = self.get_scraped_data(for_social_media, for_channel)
        try:
            return f"{scraped_data.get('title')} - {scraped_data.get('description')}"
        except Exception as e:
            pass

    @property
    def get_image_urls(self, for_social_media=None, for_channel=None):
        import pdb; pdb.set_trace()
        scraped_data = self.get_scraped_data(for_social_media, for_channel)
        try:
            return [scraped_data.get("images")]
        except Exception as e:
            pass


class ScrappedItem(models.Model):
    connector = models.ForeignKey(
        ScraperConnector, related_name="scrapped_items", on_delete=models.CASCADE
    )
    scraped_data = models.JSONField(default={})

    def __self__(self):
        return f"Scrapped Item {self.pk} from {self.connector.name}"


class SocialPost(models.Model):
    """
    A model representing a social media post.
    """

    scrapped_item = models.ForeignKey(
        ScrappedItem, related_name="social_posts", on_delete=models.CASCADE
    )
    ai_caption = models.TextField(default="", blank=True)
    caption = models.TextField()
    datetime = models.DateTimeField(auto_now_add=True)
    # post_identifier = models.CharField(blank=True, unique=True, max_length=300)
    social_media = models.CharField(
        max_length=50, choices=[("facebook", "Facebook"), ("instagram", "Instagram")]
    )
    content_type = models.CharField(
        max_length=50, choices=[("post", "Post"), ("reel", "Reel")], default="post"
    )
    sound_track = models.CharField(max_length=255, blank=True, default="")

    def __str__(self):
        return f"Posted {self.receipe_pk} on {self.social_media} at {self.datetime}"
