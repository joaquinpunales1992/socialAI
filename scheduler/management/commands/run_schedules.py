from django.core.management.base import BaseCommand
import requests
from django.conf import settings
import logging
from django.utils import timezone
from scheduler.models import SocialSchedule
from scheduler.constants import *
from connectors.utils import scrape_page
from connectors.models import ManualConnector, ScraperConnector, SocialPost, ScrappedItem

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "Run due scheduled social media posts using cron schedule."

    def handle(self, *args, **kwargs):
        now = timezone.now()
        schedules = SocialSchedule.objects.filter(active=True)

        for schedule in schedules:
            
            if not schedule.is_due(now):
                logger.info(f"Skipping {schedule.id}: Not due yet.")
                continue

            social_media = schedule.social_media.lower()
            channel = schedule.social_media_channel.lower()

            logger.info(f"Running: {social_media} - {channel}")

            try:
                schedule_api_token = schedule.api_key
                schedule_social_media_id = schedule.social_media_id
                schedule_default_caption = schedule.default_caption
                hashtags = schedule.get_hashtags()

                if isinstance(schedule.source, ManualConnector):
                    content_data = schedule.source.get_content_data
                    image_urls = schedule.source.get_image_urls

                elif isinstance(schedule.source, ScraperConnector):
                    content_data, scraped_item_pk = schedule.source.get_content_data(
                        for_social_media=social_media, for_channel=channel
                    )
                    image_urls = schedule.source.get_image_urls(for_social_media=social_media, for_channel=channel)

                image_urls = image_urls[:4]

                if social_media == "instagram" and channel == "reel":
                    json = {
                        "content_data": content_data,
                        "image_urls": image_urls,
                        "hashtags": hashtags,
                        "default_caption": schedule_default_caption,
                        "last_caption_generated": "",
                        "instagram_page_id": schedule_social_media_id,
                        "meta_api_key": schedule_api_token,
                        "use_ai_caption": True,
                        "last_reel_posted_sound_track": "",
                        "video_text": "",
                        "internet_images": True,
                    }
                    logger.info("Posting Instagram REEL...")
                    response = requests.post(
                        url=PUBLISH_INSTAGRAM_REEL_ENDPOINT, json=json
                    )
                    logger.info(f"RESPONSE: {response.reason}")

                if social_media == "instagram" and channel == "post":
                    json = {
                        "content_data": content_data,
                        "image_urls": image_urls,
                        "hashtags": hashtags,
                        "default_caption": schedule_default_caption,
                        "last_caption_generated": "",
                        "instagram_page_id": schedule_social_media_id,
                        "meta_api_key": schedule_api_token,
                        "use_ai_caption": True,
                    }
                    logger.info("Posting Instagram POST...")
                    
                    response = requests.post(
                        url=PUBLISH_INSTAGRAM_POST_ENDPOINT, json=json
                    )
                    logger.info(f"RESPONSE: {response.reason}")

                elif social_media == "facebook" and channel == "reel":
                    json = {
                        "content_data": content_data,
                        "image_urls": image_urls,
                        "hashtags": hashtags,
                        "default_caption": schedule_default_caption,
                        "facebook_page_id": schedule_social_media_id,
                        "meta_api_key": schedule_api_token,
                        "use_ai_caption": True,
                        "last_reel_posted_sound_track": "",
                        "last_caption_generated": "",
                        "video_text": "",
                        "internet_images": True,
                    }
                    logger.info("Posting Facebook REEL...")
                    response = requests.post(
                        url=PUBLISH_FACEBOOK_REEL_ENDPOINT, json=json
                    )
                    logger.info(f"RESPONSE: {response.reason}")

                elif social_media == "facebook" and channel == "post":
                    json = {
                        "content_data": content_data,
                        "image_urls": image_urls,
                        "hashtags": hashtags,
                        "default_caption": schedule_default_caption,
                        "last_caption_generated": "string",
                        "facebook_page_id": schedule_social_media_id,
                        "meta_api_key": schedule_api_token,
                        "use_ai_caption": True,
                        "internet_images": True,
                    }
                    logger.info("Posting Facebook POST...")
                    
                    response = requests.post(
                        url=PUBLISH_FACEBOOK_POST_ENDPOINT, json=json
                    )
                    logger.info(f"RESPONSE: {response.reason}")  
                else:
                    self.stdout.write(
                        logger.warning(f"Unknown combo: {social_media} - {channel}")
                    )
                    continue

                # Record the posted content
                scraped_item = ScrappedItem.objects.get(pk=scraped_item_pk)
                SocialPost.objects.create(
                    scrapped_item=scraped_item,
                    ai_caption="",
                    caption="",
                    datetime=now,
                    social_media=social_media,
                    content_type=channel,
                    sound_track="",
                )

                # Mark as run
                schedule.last_run = now
                schedule.save()

            except Exception as e:
                logger.error(f"Error on {schedule.id}: {str(e)}")
