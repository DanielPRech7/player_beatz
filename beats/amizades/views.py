from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import ListView, View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth import get_user_model
from django.db.models import Q
from django.contrib import messages
from .models import Amizade

User = get_user_model()

class ListaUsuariosView(LoginRequiredMixin, ListView):

    model = User
    template_name = 'amizades/lista_usuarios.html'
    context_object_name = 'todos_usuarios'
    paginate_by = 15

    def get_queryset(self):
        return User.objects.exclude(pk=self.request.user.pk).order_by('username')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user

        context['solicitacoes_recebidas'] = Amizade.objects.filter(
            to_user=user, 
            status=Amizade.STATUS_PENDENTE
        ).select_related('from_user__profile')
        
        context['solicitacoes_enviadas'] = Amizade.objects.filter(
            from_user=user, 
            status=Amizade.STATUS_PENDENTE
        ).values_list('to_user__pk', flat=True)
        
        amigos_aceitos_q = Q(from_user=user) | Q(to_user=user)
        context['amigos_aceitos_ids'] = Amizade.objects.filter(
            amigos_aceitos_q, 
            status=Amizade.STATUS_ACEITA
        ).values_list('from_user__pk', 'to_user__pk')
        
        amigos_ids = set()
        for id1, id2 in context['amigos_aceitos_ids']:
            amigos_ids.add(id1 if id1 != user.pk else id2)
            
        context['amigos_aceitos'] = amigos_ids

        return context


class AdicionarAmigoView(LoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        to_user_id = kwargs.get('pk')
        to_user = get_object_or_404(User, pk=to_user_id)
        from_user = request.user

        if from_user == to_user:
            messages.error(request, "Você não pode enviar uma solicitação de amizade para si mesmo.")
            return redirect('amizades:lista')

        try:
            Amizade.objects.create(from_user=from_user, to_user=to_user)
            messages.success(request, f"Solicitação de amizade enviada para {to_user.username}.")
        except Exception:
            messages.warning(request, f"A solicitação de amizade para {to_user.username} já foi enviada ou já é um amigo.")
            
        return redirect('amizades:lista')


class ResponderAmigoView(LoginRequiredMixin, View):

    def post(self, request, *args, **kwargs):
        solicitacao_id = kwargs.get('pk')
        acao = request.POST.get('acao')

        solicitacao = get_object_or_404(
            Amizade, 
            pk=solicitacao_id, 
            to_user=request.user, 
            status=Amizade.STATUS_PENDENTE
        )
        
        if acao == 'aceitar':
            solicitacao.aceitar()
            messages.success(request, f"Solicitação de amizade de {solicitacao.from_user.username} aceita.")
        elif acao == 'recusar':
            solicitacao.recusar()
            messages.info(request, f"Solicitação de amizade de {solicitacao.from_user.username} recusada.")
        else:
            messages.error(request, "Ação inválida.")

        return redirect('amizades:lista')
