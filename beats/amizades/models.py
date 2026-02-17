from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _

User = settings.AUTH_USER_MODEL 

class Amizade(models.Model):
    
    STATUS_PENDENTE = 0
    STATUS_ACEITA = 1
    STATUS_RECUSADA = 2

    STATUS_CHOICES = (
        (STATUS_PENDENTE, _('Pendente')),
        (STATUS_ACEITA, _('Aceita')),
        (STATUS_RECUSADA, _('Recusada')),
    )

    from_user = models.ForeignKey(
        User, 
        related_name='solicitacoes_enviadas',
        on_delete=models.CASCADE,
        verbose_name=_('De')
    )
    
    to_user = models.ForeignKey(
        User, 
        related_name='solicitacoes_recebidas',
        on_delete=models.CASCADE,
        verbose_name=_('Para')
    )
    
    status = models.IntegerField(
        _('Status'),
        choices=STATUS_CHOICES,
        default=STATUS_PENDENTE
    )

    data_criacao = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = _('Amizade')
        verbose_name_plural = _('Amizades')
        unique_together = ('from_user', 'to_user')

    def __str__(self):
        return f"De: {self.from_user.username} | Para: {self.to_user.username} | Status: {self.get_status_display()}"

    def aceitar(self):
        self.status = self.STATUS_ACEITA
        self.save()

    def recusar(self):
        self.status = self.STATUS_RECUSADA
        self.save()