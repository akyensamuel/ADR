from django.test import TestCase

from accounts.models import User


class UserModelTests(TestCase):
	def test_user_role_defaults_to_patient(self):
		user = User.objects.create_user(username='alice', password='secret123')

		self.assertEqual(User.Role.PATIENT, user.role)
		self.assertEqual('alice (Patient)', str(user))

	def test_user_can_be_clinician(self):
		user = User.objects.create_user(username='bob', password='secret123', role=User.Role.CLINICIAN)

		self.assertEqual(User.Role.CLINICIAN, user.role)
		self.assertEqual('bob (Clinician)', str(user))
