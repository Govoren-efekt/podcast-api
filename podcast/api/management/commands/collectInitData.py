from django.core.management.base import BaseCommand, CommandError
from podcast.api.models import Podcast, RssItem
import feedparser
from django.utils.html import strip_tags
from datetime import datetime
from time import mktime
import uuid
from django.utils.timezone import make_aware

"""
a basic map to populate db
each podcast name as key contains following entry as value

    base_url
    rss_link
"""
podcasts = {
    'Talk python to me': [
        'https://talkpython.fm',
        'https://talkpython.fm/episodes/rss',
        1
    ],
    'Djangochat': [
        'https://djangochat.com/',
        'https://feeds.simplecast.com/WpQaX_cs',
        1
    ],
    'Python podcast init': [
        'https://www.pythonpodcast.com/',
        'https://www.pythonpodcast.com/feed/mp3/',
        1
    ],
    'Test & code': [
        'https://testandcode.com/',
        'https://testandcode.com/rss',
        1
    ],
    'Friday afternoon deploy': [
        'https://friday.hirelofty.com',
        'https://feeds.simplecast.com/7if5txYU',
        1
    ],
    'Beyond the todo list': [
        'https://beyondthetodolist.com',
        'https://beyondthetodolist.com/rss',
        2
    ],
    'Masters of Scale': [
        'https://mastersofscale.com/',
        'https://rss.art19.com/masters-of-scale',
        2
    ],
    'Saas interviews with ceos, startups, founders': [
        'https://nathanlatkathetop.libsyn.com/',
        'https://nathanlatkathetop.libsyn.com/rss',
        2
    ]
}
    
class Command(BaseCommand):
    """
    load all rss feed items from the given podcast feed,
    loaded data would be populated into database

    this command should only be executed once for each podcast
    after the database has been initialized

    also check if the given podcast already exists if
    the list of podcast has been constantly changing

    """
    def handle(self, *args, **options):
        for name, data in podcasts.items():
            if Podcast.objects.filter(name=name).exists():
                print('Skip podcast {}, already exists in the db'
                        .format(name))
                continue
            rss_link = data[1]
            d = feedparser.parse(rss_link)
            self.collect_podcast(name, data, d)
            self.collect_rssItem(name, d)

    def collect_podcast(self, pc_name, pc_data, parsed_data):
        base_url = pc_data[0]
        rss_link = pc_data[1]
        category = pc_data[2]
        pd = Podcast()
        pd.name = pc_name
        pd.base_url = base_url.split('://')[1].split('/')[0]
        pd.rss_link = rss_link
        pd.category = category
        if hasattr(parsed_data.feed, 'description'):
            desc = parsed_data.feed.description
            splitted = desc.split()
            pd.description = ' '.join(splitted[:100]) if len(splitted) > 100 else desc
        if hasattr(parsed_data, 'etag'):
            pd.etag = parsed_data.etag
        if hasattr(parsed_data, 'modified'):
            pd.last_modified = parsed_data.modified 
        pd.save()
    
    def collect_rssItem(self, pc_name, parsed_data):
        pd = Podcast.objects.filter(name=pc_name).first()
        if pd is None:
            raise CommandError('Podcast with name {} does not exist'.format(pc_name))
        for item in parsed_data.entries:
            desc = strip_tags(item.summary)
            desc = ' '.join(desc.split()[:50]) if len(desc.split()) > 50 else desc
            if hasattr(item, 'itunes_episode'):
                eps_number = item.itunes_episode
            # converts date time tuple to datatime.datetime object
            date = datetime.fromtimestamp(mktime(item.published_parsed))
            # converts naive datetime object (without timezone info) to 
            # the one that has timezone info
            aware_datetime = make_aware(date)
            RssItem.objects.create(title = item.title, 
                            pub_date = aware_datetime,
                            description = desc, 
                            item_url = item.link,
                            episode_number = eps_number, 
                            GUID = uuid.uuid4(),
                            creator = pd)
