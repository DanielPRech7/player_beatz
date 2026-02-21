from django.urls import reverse_lazy, reverse
from django.shortcuts import redirect, get_object_or_404 
from django.views import View 
from django.views.generic import DetailView, CreateView
from django.views.decorators.http import require_POST
from django.core.mail import send_mail
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import Playlist, Song, PlaylistProgress
import logging
from django.db.models import Q, F
from beats.friendships.models import Friendship
from django.contrib.auth import get_user_model
from django.db.models import Sum
from django_filters.views import FilterView
from .filters import PlaylistFilter
from django.db.models import Q
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required

User = get_user_model()

logger = logging.getLogger(__name__)

@login_required
def favorite_playlist(request, pk):
    playlist = get_object_or_404(Playlist, pk=pk)
    if playlist.favorites.filter(id=request.user.id).exists():
        playlist.favorites.remove(request.user)
        is_favorite = False
    else:
        playlist.favorites.add(request.user)
        is_favorite = True
    return JsonResponse({'favorite': is_favorite})

class PlaylistUpdateCoverView(LoginRequiredMixin, View):
    def post(self, request, pk):
        playlist = get_object_or_404(Playlist, pk=pk)
        if 'new_cover' in request.FILES:
            playlist.cover = request.FILES['new_cover']
            playlist.save()
            messages.success(request, "Cover updated successfully!")
        else:
            messages.error(request, "No file selected.")
        return redirect('playlist_detail', pk=pk)
    
class PlaylistListView(FilterView):
    model = Playlist
    template_name = 'playlist/playlist_list.html'
    context_object_name = 'playlists'
    filterset_class = PlaylistFilter

    def get_queryset(self):
        queryset = Playlist.objects.annotate(
            total_time=Sum('playlistprogress__seconds_watched')
        )
        order = self.request.GET.get('sort_time')
        if order == 'most_time':
            queryset = queryset.order_by('-total_time')
        elif order == 'least_time':
            queryset = queryset.order_by('total_time')
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        most_listened = Playlist.objects.annotate(
            total_time=Sum('playlistprogress__seconds_watched')
        ).order_by('-total_time').first()
        context['most_listened_id'] = most_listened.id if most_listened else None
        return context

@require_POST
def update_playlist_time(request, pk):
    if not request.user.is_authenticated:
        return JsonResponse({'status': 'error', 'message': 'Login required'}, status=401)

    new_seconds = int(request.POST.get('seconds', 0))

    if new_seconds > 0:
        progress, created = PlaylistProgress.objects.get_or_create(
            user=request.user,
            playlist_id=pk
        )
        progress.seconds_watched = F('seconds_watched') + new_seconds
        progress.save()

        progress.refresh_from_db()
        return JsonResponse({
            'status': 'success',
            'total_accumulated': progress.seconds_watched
        })
    return JsonResponse({'status': 'error', 'message': 'Invalid time'}, status=400)

class PlaylistDetailView(DetailView):
    model = Playlist
    template_name = 'playlist/playlist_detail.html'
    context_object_name = 'playlist'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        current_playlist = self.object
        user = self.request.user

        song_ids = current_playlist.songs.values_list('id', flat=True)

        other_playlists = Playlist.objects.filter(
            songs__id__in=song_ids
        ).exclude(id=current_playlist.id).distinct()

        context['shared_history'] = other_playlists

        if user.is_authenticated:
            friends_query = Friendship.objects.filter(
                (Q(from_user=user) | Q(to_user=user)),
                status=Friendship.Status.ACCEPTED
            ).values_list('from_user_id', 'to_user_id')

            ids_set = {uid for f_id, t_id in friends_query for uid in (f_id, t_id) if uid != user.id}

            context['last_friend_playlist'] = Playlist.objects.filter(
                playlistprogress__user_id__in=ids_set
            ).distinct().order_by('-id').first()

            progress = current_playlist.playlistprogress_set.filter(user=user).first()
            context['db_time'] = progress.seconds_watched if progress else 0
        return context

class PlaylistCreateView(CreateView):
    model = Playlist
    fields = ['name']
    template_name = 'playlist/playlist_form.html'
    success_url = reverse_lazy('playlist_list')

class PlaylistAddSongView(View):
    def post(self, request, pk):
        playlist = get_object_or_404(Playlist, pk=pk)
        song_id = request.POST.get('song_id')

        if song_id:
            song = get_object_or_404(Song, pk=song_id)
            playlist.songs.add(song)
        return redirect('playlist_detail', pk=playlist.pk)

class PlaylistShareView(View):
    def post(self, request, pk):
        playlist = get_object_or_404(Playlist, pk=pk)
        email = request.POST.get('email')

        if not email:
            messages.error(request, "Please provide your friend's email to share.")
            return redirect('playlist_detail', pk=playlist.pk)

        sender_name = request.user.username if request.user.is_authenticated else 'Someone'
        subject = f"{sender_name} shared a playlist with you"
        playlist_url = request.build_absolute_uri(reverse('playlist_detail', args=[playlist.pk]))
        message = (
            f"Hello,\n\n{sender_name} shared the playlist \"{playlist.name}\" with you.\n"
            f"See here: {playlist_url}\n\n"
            "— Beats.app"
        )

        from_email = getattr(settings, 'DEFAULT_FROM_EMAIL', None) or 'no-reply@beats.app'
        send_mail(subject, message, from_email, [email], fail_silently=False)
        messages.success(request, f"Playlist shared with {email} successfully.")

        return redirect('playlist_detail', pk=playlist.pk)