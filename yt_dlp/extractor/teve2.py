import re
from .common import InfoExtractor
from ..utils import ExtractorError

class Teve2EpisodeIE(InfoExtractor):
    # https://www.teve2.com.tr
    _BASE_URL_RE = r'https?://(www\.)?teve2\.com\.tr'
    # /diziler/guncel/adi-efsane/bolumler/adi-efsane-29-bolum-final
    # /programlar/guncel/kelime-oyunu/bolumler/kelime-oyunu-1610-bolum-13-12-2024
    _VALID_URL = _BASE_URL_RE + r'/(diziler|programlar)/(guncel|arsiv)/[a-z\-]+/bolumler/[a-z\-]+-[0-9]+-bolum(-[0-9\-]+|-final)?'

    def _extract_episode(self, url):
        # extract episode info
        webpage = self._download_webpage(url, None)
        id = self._html_search_regex(r'data-content-id="([a-z0-9]+)"', webpage, None)
        if id is None or id == '':
            raise ExtractorError(f'Cannot get id from webpage')

        title = self._html_search_regex(r'data-original-name="(.*?)"', webpage, None)
        if title is None or title == '':
            raise ExtractorError(f'Cannot get title from webpage')

        # get video url
        json = self._download_json(f"https://www.teve2.com.tr/action/media/{id}", id)
        url = json['Media']['Link']['ServiceUrl'] + json['Media']['Link']['SecurePath']
        if url is None or url == '':
            raise ExtractorError(f'Cannot get video url')

        # TODO: episode_number
        # TODO:
        #   see https://github.com/yt-dlp/yt-dlp/blob/master/yt_dlp/extractor/common.py#L119-L440
        return {
            'id': id,
            'title': title,
            'url': url,
        }

    def _real_extract(self, url):
        return self._extract_episode(url)

class Teve2PlaylistIE(Teve2EpisodeIE):
    # https://www.teve2.com.tr
    _BASE_URL_RE = r'https?://(www\.)?teve2\.com\.tr'
    # /programlar/guncel/kelime-oyunu/bolumler/kelime-oyunu-1610-bolum-13-12-2024
    _VALID_URL = _BASE_URL_RE + r'/(diziler|programlar)/(guncel|arsiv)/[a-z\-]+/bolumler([?].*)?'

    def _real_extract(self, url):
        category = url.split('/')[3]    # diziler, programlar
        subcategory = url.split('/')[4] # guncel, arsiv
        slug = url.split('/')[5]
        # extract episodes
        webpage = self._download_webpage(url, None)

        entries = []
        for r in re.finditer(rf'href="(/{category}/{subcategory}/{slug}/bolumler/{slug}-.*?)"', webpage):
            episodeUrl = f"https://www.teve2.com.tr{r.group(1)}"
            episode = self._extract_episode(episodeUrl)
            entries.append(episode)

        return {
            '_type': 'playlist',
            'id': slug,
            'title': slug,
            'entries': entries,
        }

