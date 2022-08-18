from django.db import models


class Place(models.Model):
    address = models.TextField(
        'адрес',
        max_length=200,
        unique=True
    )
    longitude = models.DecimalField(
        'долгота',
        max_digits=9,
        decimal_places=6,
        null=True,
        blank=True
    )
    latitude = models.DecimalField(
        'широта',
        max_digits=9,
        decimal_places=6,
        null=True,
        blank=True
    )
    saved_at = models.DateTimeField(
        'координаты запрошены',
        auto_now=True
    )

    class Meta:
        verbose_name = 'место'
        verbose_name_plural = 'места'

    def __str__(self):
        return f"{self.address} ({self.longitude}, {self.latitude})"
