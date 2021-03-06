def player_for_user(user):
    from music import models
    try:
        player = models.Player.objects.get(user=user, type='B')
    except models.Player.DoesNotExist:
        player = models.Player(user=user, type='B')
        playlist = models.Playlist(user=user)
        playlist.save()

        player.playlist = playlist
        player.save()
    return player


def duration(length):
    import datetime

    duration = str(datetime.timedelta(seconds=length))
    return duration[2:] if duration[0:2] == '0:' else duration


def artists(request):
    # tags backend
    from music.models import Artist, Collection
    artists = Artist.objects.exclude(album=None).filter(collection__disabled=False).values('id', 'name', 'sortname')

    from django.urls import reverse
    url = reverse('music:artist_detail', args=(0,))

    def add_url_to_tag_artist(dict_item):
        #dict_item['url'] = reverse('music:artist_detail', args=(dict_item['id'],))
        dict_item['url'] = url.replace('0', str(dict_item['id']))
        return dict_item

    artists = map(add_url_to_tag_artist, artists)


    # files backend
    from music.backend.files import artists_tuple

    dirs = []
    for collection in Collection.objects.filter(backend='F', disabled=False):
        dirs += artists_tuple(collection)

    sort_key = "sortname"
    if hasattr(request, "user") and \
       hasattr(request.user, "settings") and \
       hasattr(request.user.settings, "ordering"):
        sort_key = request.user.settings.ordering

    def add_sortkeyname_to_tag_artist(dict_item):
        dict_item['sortkeyname'] = dict_item[sort_key]
        return dict_item
    artists = map(add_sortkeyname_to_tag_artist, artists)

    artists = sorted(list(artists) + dirs, key=lambda a: a[sort_key])

    return artists


def register_playback(track, user):
    if user.is_authenticated:
        from music.models import LastPlayed
        try:
            last = LastPlayed.objects.get(user=user)
        except LastPlayed.DoesNotExist:
            last = LastPlayed(user=user)
        last.set_track(track)
        last.save()


def swap_playlist_tracks(a, b):
    sort_a = a.sort_order
    sort_b = b.sort_order

    a.sort_order = sort_b
    b.sort_order = sort_a

    a.save()
    b.save()
