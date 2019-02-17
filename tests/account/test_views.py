import re

from django.core import mail
from django.test import TestCase

from account.models import Account


class SendTokenAPIViewTestCase(TestCase):

	def setUp(self):
		Account.objects.create(**{
			'username': 'test_user',
			'email': 'test.user@gmail.com',
			'password': 'test_password'
		})

	def test_post_201_created(self):
		response = self.client.post('/api/v1/accounts/send/token', data={
			'username': 'test_user'
		})
		self.assertEqual(response.status_code, 201)
		self.assertTrue('detail' in response.json())

	def test_post_404_not_found(self):
		response = self.client.post('/api/v1/accounts/send/token', data={
			'username': 'test_user1'
		})
		self.assertEqual(response.status_code, 404)
		self.assertTrue('detail' in response.json())

	def test_post_400_bad(self):
		response = self.client.post('/api/v1/accounts/send/token')
		self.assertEqual(response.status_code, 400)
		self.assertTrue('detail' in response.json())


class AccountDeleteAPIViewTestCase(TestCase):

	def setUp(self):
		Account.create(**{
			'username': 'test_user',
			'email': 'test.user@gmail.com',
			'password': 'test_password'
		}).save()

	def test_post_201_created(self):
		response = self.client.post('/api/v1/auth/login/', data={
			'username': 'test_user',
			'password': 'test_password'
		})
		response = self.client.post('/api/v1/accounts/delete', **{
			'HTTP_AUTHORIZATION': 'Token {}'.format(response.json().get('key'))
		})
		self.assertEqual(response.status_code, 201)
		self.assertTrue('detail' in response.json())

	def test_post_401_unauthorized(self):
		response = self.client.post('/api/v1/accounts/delete')
		self.assertEqual(response.status_code, 401)
		self.assertTrue('detail' in response.json())


class AccountCreateAPIViewTestCase(TestCase):

	def test_post_201_created(self):
		response = self.client.post('/api/v1/accounts/create', {
			'username': 'test_user',
			'email': 'test.user@gmail.com'
		})
		self.assertEqual(response.status_code, 201)
		self.assertTrue('detail' in response.json())

	def test_post_400_bad_username_is_not_provided(self):
		response = self.client.post('/api/v1/accounts/create', {
			'email': 'test.user@gmail.com'
		})
		self.assertEqual(response.status_code, 400)
		self.assertTrue('username' in response.json())

	def test_post_400_bad_email_is_not_provided(self):
		response = self.client.post('/api/v1/accounts/create', {
			'username': 'test_user'
		})
		self.assertEqual(response.status_code, 400)
		self.assertTrue('non_field_errors' in response.json())


class ResetPasswordAPIViewTestCase(TestCase):

	def setUp(self):
		Account.objects.create(**{
			'username': 'test_user',
			'email': 'test.user@gmail.com',
			'password': 'test_password'
		})

	def test_post_201_created(self):
		response = self.client.post('/api/v1/accounts/send/token', data={
			'username': 'test_user'
		})
		self.assertEqual(response.status_code, 201)
		self.assertTrue('detail' in response.json())

		token = re.search(r'token:\s*\n\s*([a-z0-9]{64})', str(mail.outbox[0].body)).group(1)

		response = self.client.post('/api/v1/accounts/password/reset', data={
			'username': 'test_user',
			'new_password': 'new_test_password',
			'new_password_confirm': 'new_test_password',
			'confirmation_token': token
		})
		self.assertEqual(response.status_code, 201)
		self.assertTrue('detail' in response.json())

	def test_post_400_username_is_not_provided(self):
		response = self.client.post('/api/v1/accounts/password/reset')
		self.assertEqual(response.status_code, 400)
		self.assertTrue('detail' in response.json())

	def test_post_404_account_is_not_found(self):
		response = self.client.post('/api/v1/accounts/password/reset', data={
			'username': 'some_username'
		})
		self.assertEqual(response.status_code, 404)
		self.assertTrue('detail' in response.json())

	def test_post_400_missing_confirmation_token(self):
		response = self.client.post('/api/v1/accounts/password/reset', data={
			'username': 'test_user'
		})
		self.assertEqual(response.status_code, 400)
		self.assertTrue('detail' in response.json())

	def test_post_400_token_token_is_incorrect(self):
		response = self.client.post('/api/v1/accounts/password/reset', data={
			'username': 'test_user',
			'confirmation_token': 'some1token'
		})
		self.assertEqual(response.status_code, 400)
		self.assertTrue('detail' in response.json())

	def test_post_400_missing_new_password(self):
		response = self.client.post('/api/v1/accounts/send/token', data={
			'username': 'test_user'
		})
		self.assertEqual(response.status_code, 201)
		self.assertTrue('detail' in response.json())

		token = re.search(r'token:\s*\n\s*([a-z0-9]{64})', str(mail.outbox[0].body)).group(1)

		response = self.client.post('/api/v1/accounts/password/reset', data={
			'username': 'test_user',
			'new_password_confirm': 'new_test_password',
			'confirmation_token': token
		})
		self.assertEqual(response.status_code, 400)
		self.assertTrue('detail' in response.json())

	def test_post_400_missing_password_confirm(self):
		response = self.client.post('/api/v1/accounts/send/token', data={
			'username': 'test_user'
		})
		self.assertEqual(response.status_code, 201)
		self.assertTrue('detail' in response.json())

		token = re.search(r'token:\s*\n\s*([a-z0-9]{64})', str(mail.outbox[0].body)).group(1)

		response = self.client.post('/api/v1/accounts/password/reset', data={
			'username': 'test_user',
			'new_password': 'new_test_password',
			'confirmation_token': token
		})
		self.assertEqual(response.status_code, 400)
		self.assertTrue('detail' in response.json())

	def test_post_400_password_confirmation_failed(self):
		response = self.client.post('/api/v1/accounts/send/token', data={
			'username': 'test_user'
		})
		self.assertEqual(response.status_code, 201)
		self.assertTrue('detail' in response.json())

		token = re.search(r'token:\s*\n\s*([a-z0-9]{64})', str(mail.outbox[0].body)).group(1)

		response = self.client.post('/api/v1/accounts/password/reset', data={
			'username': 'test_user',
			'new_password': 'new_test_password',
			'new_password_confirm': 'new_test_password_another',
			'confirmation_token': token
		})
		self.assertEqual(response.status_code, 400)
		self.assertTrue('detail' in response.json())