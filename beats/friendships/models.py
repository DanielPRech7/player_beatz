from django.db import models
from django.conf import settings

User = settings.AUTH_USER_MODEL 

class Friendship(models.Model):

    class Status(models.IntegerChoices):
        PENDING = 0, 'Pending'
        ACCEPTED = 1, 'Accepted'
        REJECTED = 2, 'Rejected'

    from_user = models.ForeignKey(
        User, 
        related_name='sent_requests',
        on_delete=models.CASCADE,
        verbose_name='From'
    )
    
    to_user = models.ForeignKey(
        User, 
        related_name='received_requests',
        on_delete=models.CASCADE,
        verbose_name='To'
    )
    
    status = models.IntegerField(
        'Status',
        choices=Status.choices,
        default=Status.PENDING
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Friendship'
        verbose_name_plural = 'Friendships'
        unique_together = ('from_user', 'to_user')

    def __str__(self):
        return f"{self.from_user} -> {self.to_user} ({self.get_status_display()})"

    @property
    def is_accepted(self):
        return self.status == self.Status.ACCEPTED

    def accept(self):
        self.status = self.Status.ACCEPTED
        self.save(update_fields=['status'])

    def reject(self):
        self.status = self.Status.REJECTED
        self.save(update_fields=['status'])