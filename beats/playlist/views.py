from django.urls import reverse_lazy, reverse
from django.shortcuts import redirect, get_object_or_404 
from django.views import View 
from django.views.generic import ListView, DetailView, CreateView
from django.core.mail import send_mail
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import Playlist, Musica, PlaylistRating, PlaylistProgress
import logging
from django.db.models import Q, F
from beats.amizades.models import Amizade
from django.contrib.auth import get_user_model
from django.db.models import Sum
from django.views.generic import UpdateView
from django_filters.views import FilterView
from .filters import PlaylistFilter
from django.db.models import Q, Avg, Count
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required

from django.http import JsonResponse
from django.views.decorators.http import require_POST

User = get_user_model()

logger = logging.getLogger(__name__)

@login_required
def favoritar_playlist(request, pk):
    playlist = get_object_or_404(Playlist, pk=pk)
    if playlist.favoritos.filter(id=request.user.id).exists():
        playlist.favoritos.remove(request.user)
        favorito = False
    else:
        playlist.favoritos.add(request.user)
        favorito = True
    return JsonResponse({'favorito': favorito})

class PlaylistListView(ListView):
    model = Playlist
    template_name = 'playlist/playlist_list.html'
    context_object_name = 'playlists'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        mais_ouvida = Playlist.objects.annotate(
            tempo_total=Sum('playlistprogress__segundos_assistidos')
        ).order_by('-tempo_total').first()

        if mais_ouvida and mais_ouvida.tempo_total:
            context['id_mais_ouvida'] = mais_ouvida.id
        else:
            context['id_mais_ouvida'] = None
            
        return context

    def get(self, request, *args, **kwargs):
        logger.info("Playlist list view foi acessada.")
        return super().get(request, *args, **kwargs)
    
class PlaylistListView(FilterView): # Alterado de ListView para FilterView
    model = Playlist
    template_name = 'playlist/playlist_list.html'
    context_object_name = 'playlists'
    filterset_class = PlaylistFilter

    def get_queryset(self):
        queryset = Playlist.objects.annotate(
            tempo_total=Sum('playlistprogress__segundos_assistidos')
        )
        
        ordem = self.request.GET.get('sort_tempo')
        if ordem == 'mais_tempo':
            queryset = queryset.order_by('-tempo_total')
        elif ordem == 'menos_tempo':
            queryset = queryset.order_by('tempo_total')
            
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        mais_ouvida = Playlist.objects.annotate(
            tempo_total=Sum('playlistprogress__segundos_assistidos')
        ).order_by('-tempo_total').first()
        
        context['id_mais_ouvida'] = mais_ouvida.id if mais_ouvida else None
        return context

class PlaylistUpdateCapaView(LoginRequiredMixin, View):
    def post(self, request, pk):
        playlist = get_object_or_404(Playlist, pk=pk)
        if 'nova_capa' in request.FILES:
            playlist.capa = request.FILES['nova_capa']
            playlist.save()
            messages.success(request, "Capa atualizada com sucesso!")
        else:
            messages.error(request, "Nenhum arquivo selecionado.")
            
        return redirect('playlist_detail', pk=pk)

@require_POST
def atualizar_tempo_playlist(request, pk):
    if not request.user.is_authenticated:
        return JsonResponse({'status': 'error', 'message': 'Login necessário'}, status=401)
    
    segundos_novos = int(request.POST.get('segundos', 0))
    
    if segundos_novos > 0:
        progress, created = PlaylistProgress.objects.get_or_create(
            user=request.user,
            playlist_id=pk
        )
        progress.segundos_assistidos = F('segundos_assistidos') + segundos_novos
        progress.save()
        
        progress.refresh_from_db()
        return JsonResponse({
            'status': 'success', 
            'total_acumulado': progress.segundos_assistidos
        })
    return JsonResponse({'status': 'error', 'message': 'Tempo inválido'}, status=400)

class PlaylistDetailView(DetailView):
    model = Playlist
    template_name = 'playlist/playlist_detail.html'
    context_object_name = 'playlist'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        playlist_atual = self.object
        user = self.request.user

        # 1. Músicas da playlist atual
        musicas_ids = playlist_atual.musicas.values_list('id', flat=True)

        # 2. Buscar outras playlists que contenham essas músicas
        # Filtramos playlists que não sejam a atual e que tenham músicas em comum
        outras_playlists = Playlist.objects.filter(
            musicas__id__in=musicas_ids
        ).exclude(id=playlist_atual.id).distinct()

        # Se você tiver um campo 'criador' no seu Model Playlist, 
        # use .select_related('criador') para performance.
        
        context['historico_compartilhado'] = outras_playlists

        # 3. Lógica de Amigos (Sua lógica original corrigida)
        if user.is_authenticated:
            amigos_query = Amizade.objects.filter(
                (Q(from_user=user) | Q(to_user=user)),
                status=Amizade.STATUS_ACEITA
            ).values_list('from_user_id', 'to_user_id')

            # Simplificando a extração de IDs de amigos
            ids_set = {uid for f_id, t_id in amigos_query for uid in (f_id, t_id) if uid != user.id}

            context['ultima_playlist_amigo'] = Playlist.objects.filter(
                playlistprogress__user_id__in=ids_set
            ).distinct().order_by('-id').first()

            # Progresso do usuário logado
            progresso = playlist_atual.playlistprogress_set.filter(user=user).first()
            context['tempo_do_banco'] = progresso.segundos_assistidos if progresso else 0
        
        # 4. Avaliações (Opcional, mas recomendado para o seu template)
        context['media_avaliacoes'] = playlist_atual.playlistrating_set.aggregate(Avg('nota'))['nota__avg'] or 0
        context['todas_avaliacoes'] = playlist_atual.playlistrating_set.all().order_by('-data_avaliacao')

        return context

class AvaliarPlaylistView(LoginRequiredMixin, View):
    def post(self, request, pk):
        playlist = get_object_or_404(Playlist, pk=pk)
        nota = request.POST.get('nota')
        comentario = request.POST.get('comentario', '')

        if not nota or not nota.isdigit() or not (1 <= int(nota) <= 5):
            messages.error(request, 'Por favor, forneça uma nota válida.')
            return redirect('playlist_detail', pk=pk)

        rating, created = PlaylistRating.objects.update_or_create(
            user=request.user,
            playlist=playlist,
            defaults={'nota': nota, 'comentario': comentario}
        )

        if created:
            messages.success(request, 'Avaliação criada com sucesso!')
        else:
            messages.success(request, 'Avaliação atualizada com sucesso!')

        return redirect('playlist_detail', pk=pk)

class PlaylistCreateView(CreateView):
    model = Playlist
    fields = ['nome']
    template_name = 'playlist/playlist_form.html'
    success_url = reverse_lazy('playlist_list') 

class PlaylistAddMusicaView(View):
    def post(self, request, pk):
        playlist = get_object_or_404(Playlist, pk=pk)
        musica_id = request.POST.get('musica_id')
        
        if musica_id:
            musica = get_object_or_404(Musica, pk=musica_id)
            playlist.musicas.add(musica)
        return redirect('playlist_detail', pk=playlist.pk)

class PlaylistShareView(View):

    def post(self, request, pk):
        playlist = get_object_or_404(Playlist, pk=pk)
        email = request.POST.get('email')

        if not email:
            messages.error(request, "Informe o e-mail do amigo para compartilhar.")
            return redirect('playlist_detail', pk=playlist.pk)

        sender_name = request.user.username if request.user.is_authenticated else 'Alguém'
        subject = f"{sender_name} compartilhou uma playlist com você"
        playlist_url = request.build_absolute_uri(reverse('playlist_detail', args=[playlist.pk]))
        message = (
            f"Olá,\n\n{sender_name} compartilhou a playlist \"{playlist.nome}\" com você.\n"
            f"Veja aqui: {playlist_url}\n\n" 
            "— Beats.app"
        )

        from_email = getattr(settings, 'DEFAULT_FROM_EMAIL', None) or 'no-reply@beats.app'
        send_mail(subject, message, from_email, [email], fail_silently=False)
        messages.success(request, f"Playlist compartilhada com {email} com sucesso.")

        return redirect('playlist_detail', pk=playlist.pk)