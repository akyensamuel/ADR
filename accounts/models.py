from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
	class Role(models.TextChoices):
		PATIENT = 'patient', 'Patient'
		CLINICIAN = 'clinician', 'Clinician'

	role = models.CharField(max_length=20, choices=Role.choices, default=Role.PATIENT)

	def __str__(self) -> str:
		return f'{self.username} ({self.get_role_display()})'
