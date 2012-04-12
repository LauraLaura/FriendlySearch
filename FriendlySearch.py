"""
This work is licensed under the Creative Commons Attribution-NonCommercial-ShareAlike 3.0 Unported License.
To view a copy of this license visit http://creativecommons.org/licenses/by-nc-sa/3.0/

Created By Laura Coleman
April 2012
"""

import gdata.youtube
import gdata.youtube.service
yt_service = gdata.youtube.service.YouTubeService()
yt_service.ssl = True


"""
friendly_search searches youtube for videos related to an input query string, and returns a list of information
about related videos.  The returned information includes the title, url, youtube rating, friendly rating (based
on the user's social network), and a list of the user's immediate friends who have liked the video.

Videos that have been liked people within 5 degrees of friendship (i.e. a friend of a friend of a friend of a
friend of a friend) are returned 1st, followed by videos that haven't been liked by people within 5 degrees of
friendship.

Videos that have been liked are sorted by their friendly ratings, which are calculated by the following
formula:
    (2 if current user likes, 0 if not)  +  1 * # of 1st degree friends who like
    +  0.5 * # of 2nd degree friends who like  +  0.25 * # of 3rd degree friends who like
    +  0.125 * # of 4th degree friends who like  +  0.0625 * # of 5th degree friends who like

Videos that haven't been liked are sorted by their YouTube ratings.


Inputs:  query: the string to search for
         social_network: a dictionary of people and who they are friends with, in the following format:
            {person1: [friend1, friend2], person2: [friend1, friend2, friend3], ...}
         likes: a dictionary of people and what YouTube videos they like, in the following format:
            {person1: [video1, video2, video3], person2: [video1], ...}
         current_user: the name of the person who is doing the search.
Output:  a list of youtube videos in the following format:
            [ [title, url, youtube_rating, friendly_rating, [friends_who_like]], [title, url, youtube_rating, friendly_rating, [friends_who_like]]... ]
"""
def friendly_search(query, social_network, likes, current_user):
    results_youtube = search_you_tube(query)  #format is [[title, url, youtube_rating],[title, url, youtube_rating]...]
    results_with_likes = []   #format is [[title, url, youtube_rating, friendly_rating, [friends_who_like],[title, url, youtube_rating, friendly_rating, [friends_who_like]...]
    results_no_likes = []

    #friends of current user
    friend_list_deg1 = social_network[current_user]    #format is [ friend1, friend2,... ]

    already_listed = [current_user]
    union(already_listed, friend_list_deg1)

    #friends of friends of current user, no duplicates, leave out people who are in lower-degree lists
    friend_list_deg2 = []
    for friend in friend_list_deg1:
        for f in social_network[friend]:
            if f not in already_listed:
                friend_list_deg2.append(f)
                already_listed.append(f)

    friend_list_deg3 = []
    for friend in friend_list_deg2:
        for f in social_network[friend]:
            if f not in already_listed:
                friend_list_deg3.append(f)
                already_listed.append(f)

    friend_list_deg4 = []
    for friend in friend_list_deg3:
        for f in social_network[friend]:
            if f not in already_listed:
                friend_list_deg4.append(f)
                already_listed.append(f)

    friend_list_deg5 = []
    for friend in friend_list_deg4:
        for f in social_network[friend]:
            if f not in already_listed:
                friend_list_deg5.append(f)
                already_listed.append(f)


    #for each video, get friendly_rating and list of 1st degree friends who like it
    for entry in results_youtube:
        likes_deg1 = []
        for friend in friend_list_deg1:
            if entry[1] in likes[friend]:
                likes_deg1.append(friend)

        if entry[1] in likes[current_user]:
            friendly_rating = 2 + len(likes_deg1)
        else:
            friendly_rating = len(likes_deg1)

        likers = 0
        for friend in friend_list_deg2:
            if entry[1] in likes[friend]:
                likers = likers + 1
        friendly_rating = friendly_rating + 0.5 * likers

        likers = 0
        for friend in friend_list_deg3:
            if entry[1] in likes[friend]:
                likers = likers + 1
        friendly_rating = friendly_rating + 0.25 * likers

        likers = 0
        for friend in friend_list_deg4:
            if entry[1] in likes[friend]:
                likers = likers + 1
        friendly_rating = friendly_rating + 0.125 * likers

        likers = 0
        for friend in friend_list_deg5:
            if entry[1] in likes[friend]:
                likers = likers + 1
        friendly_rating = friendly_rating + 0.0625 * likers

        if friendly_rating != 0:
            results_with_likes.append([entry[0], entry[1], entry[2], friendly_rating, likes_deg1])
        else:
            results_no_likes.append([entry[0], entry[1], entry[2], 0, []])


    #sort results_with_likes in order of friendly_rating
    sorted_results_with_likes = quicksort(results_with_likes, 3)

    #sort results_no_likes in order of youtube rating
    sorted_results_no_likes = quicksort(results_no_likes, 2)

    return sorted_results_with_likes + sorted_results_no_likes


"""
search_you_tube searches youtube for videos related to an input query string, and returns a list of information
about related videos, including title, url, and youtube rating.

If a video has no youtube rating, it is given a rating of 2.5 out of 5.0.

Inputs:  search_terms: the string to search for
Output:  a list of youtube videos in the following format:
            [ [title, url, youtube_rating], [title, url, youtube_rating]... ]
"""
def search_you_tube(search_terms):
    yt_service = gdata.youtube.service.YouTubeService()
    query = gdata.youtube.service.YouTubeVideoQuery()
    query.vq = search_terms
    query.racy = 'include'
    feed = yt_service.YouTubeQuery(query)

    results = []
    for entry in feed.entry:
        if entry.media.title.text != None and entry.media.player.url != None:
            if entry.rating == None:
                results.append([entry.media.title.text, entry.media.player.url, 2.5])   #if not yet rated, give rating of 2.5 / 5.0
            else:
                results.append([entry.media.title.text, entry.media.player.url, entry.rating.average])
    return results


"""
quicksort sorts a list by a given element in the list.

Inputs:  list_to_sort: a list
         element_to_sort_on: the number of the element in the list to sort on
Output:  a list in the same format as the input list, sorted by the given element
"""
def quicksort(list_to_sort, element_to_sort_on):
    if (len(list_to_sort) == 0 or len(list_to_sort) == 1):
        return list_to_sort
    pivot = list_to_sort[0]
    list_less = []
    list_more = []
    for i in range(1, len(list_to_sort)):
        if list_to_sort[i][element_to_sort_on] <= pivot[element_to_sort_on]:
            list_less.append(list_to_sort[i])
        else:
            list_more.append(list_to_sort[i])
    sorted_list_more = quicksort(list_more, element_to_sort_on)
    sorted_list_more.append(pivot)
    sorted_list_less = quicksort(list_less, element_to_sort_on)
    return sorted_list_more + sorted_list_less


"""
union appends the elements in list b to list a if they aren't already there
"""
def union(a, b):
    for e in b:
        if e not in a:
            a.append(e)


"""
social_network is a dictionary that holds a list of people and who their friends are.
In this example, friendship is bidirectional (i.e. if Jay is friends with Rob, then
Rob is also friends with Jay), however Friendly Search would work equally well if
friendship were unidirectional.
"""
social_network = { 'Jay':   ['Rob', 'Erika', 'Laura', 'Susan', 'John'],
                   'Rob':   ['Jay', 'Lucy',  'James'],
                   'Erika': ['Jay', 'Laura', 'Susan'],
                   'Laura': ['Jay', 'Erika', 'Susan', 'John', 'Lucy'],
                   'Susan': ['Jay', 'Laura', 'Erika'],
                   'John':  ['Jay', 'Laura', 'Lucy'],
                   'Lucy':  ['Rob', 'Laura', 'John'],
                   'James': ['Rob'],
                   'Chuck': ['Cathy', 'Ryan'],
                   'Cathy': ['Chuck', 'Paula'],
                   'Ryan':  ['Chuck'],
                   'Paula': ['Cathy', 'James']
                 }

"""
likes is a dictionary that holds a list of people and what YouTube videos they like.
"""
likes = { 'Jay':   ['https://www.youtube.com/watch?v=WJxyxdK_-xA&feature=youtube_gdata_player',
                    'https://www.youtube.com/watch?v=BQHMLD9bwq4&feature=youtube_gdata_player',
                    'https://www.youtube.com/watch?v=_LXuAT9R1-E&feature=youtube_gdata_player',
                    'https://www.youtube.com/watch?v=IYZNchSxaHk&feature=youtube_gdata_player'],
          'Rob':   ['https://www.youtube.com/watch?v=PckSUEQu3F8&feature=youtube_gdata_player'],
          'Erika': ['https://www.youtube.com/watch?v=WJxyxdK_-xA&feature=youtube_gdata_player'],
          'Laura': ['https://www.youtube.com/watch?v=_LXuAT9R1-E&feature=youtube_gdata_player',
                    'https://www.youtube.com/watch?v=IYZNchSxaHk&feature=youtube_gdata_player'],
          'Susan': ['https://www.youtube.com/watch?v=BQHMLD9bwq4&feature=youtube_gdata_player',
                    'https://www.youtube.com/watch?v=IYZNchSxaHk&feature=youtube_gdata_player'],
          'John':  ['https://www.youtube.com/watch?v=WJxyxdK_-xA&feature=youtube_gdata_player'],
          'Lucy':  [],
          'James': ['https://www.youtube.com/watch?v=PckSUEQu3F8&feature=youtube_gdata_player',
                    'https://www.youtube.com/watch?v=BQHMLD9bwq4&feature=youtube_gdata_player'],
          'Chuck': ['https://www.youtube.com/watch?v=IYZNchSxaHk&feature=youtube_gdata_player'],
          'Cathy': ['https://www.youtube.com/watch?v=IYZNchSxaHk&feature=youtube_gdata_player',
                    'https://www.youtube.com/watch?v=WJxyxdK_-xA&feature=youtube_gdata_player'],
          'Ryan':  [],
          'Paula': ['https://www.youtube.com/watch?v=_LXuAT9R1-E&feature=youtube_gdata_player',
                    'https://www.youtube.com/watch?v=WJxyxdK_-xA&feature=youtube_gdata_player',
                    'https://www.youtube.com/watch?v=PckSUEQu3F8&feature=youtube_gdata_player']
        }

print friendly_search('udacity cs101', social_network, likes, 'Chuck')
