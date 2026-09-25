from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase

from Projects.models import Project


class DashboardAuthenticationTests(TestCase):
	def setUp(self):
		self.user = get_user_model().objects.create_user(
			username='admin-test',
			password='correct-password',
		)

	def test_admin_entry_shows_login_page(self):
		response = self.client.get('/admin/')

		self.assertEqual(response.status_code, 200)
		self.assertContains(response, 'Admin access')

	def test_invalid_credentials_return_login_page(self):
		response = self.client.post('/admin/', {
			'username': self.user.username,
			'password': 'wrong-password',
		})

		self.assertEqual(response.status_code, 200)
		self.assertContains(response, 'Invalid username or password')

	def test_valid_credentials_redirect_to_overview(self):
		response = self.client.post('/admin/', {
			'username': self.user.username,
			'password': 'correct-password',
		})

		self.assertRedirects(response, '/dashboard/overview/')

	def test_dashboard_pages_require_login(self):
		for path in ('/dashboard/overview/', '/dashboard/projects/', '/dashboard/contacts/'):
			response = self.client.get(path)
			self.assertRedirects(response, f'/dashboard/?next={path}')

	def test_logout_returns_to_login(self):
		self.client.force_login(self.user)

		response = self.client.get('/dashboard/logout/')

		self.assertRedirects(response, '/dashboard/')

	def test_authenticated_user_can_add_project_with_cover_photo(self):
		self.client.force_login(self.user)
		cover_photo = SimpleUploadedFile(
			'cover.gif',
			b'GIF89a\x01\x00\x01\x00\x80\x00\x00\x00\x00\x00\xff\xff\xff!\xf9\x04\x01\x00\x00\x00\x00,\x00\x00\x00\x00\x01\x00\x01\x00\x00\x02\x02D\x01\x00;',
			content_type='image/gif',
		)

		response = self.client.post('/dashboard/projects/', {
			'title': 'New Portfolio Project',
			'description': 'A project description.',
			'problem': 'The original problem.',
			'solution': 'The implemented solution.',
			'technologies': 'Django, Tailwind',
			'url': 'https://example.com/project',
			'date': '2026-09-10',
			'cover_photo': cover_photo,
		}, format='multipart')

		self.assertRedirects(response, '/dashboard/projects/')
		project = Project.objects.get(title='New Portfolio Project')
		self.assertEqual(project.technologies, ['Django', 'Tailwind'])
		self.assertTrue(project.cover_photo.name.startswith('projects/cover'))

	def test_invalid_project_submission_renders_errors(self):
		self.client.force_login(self.user)

		response = self.client.post('/dashboard/projects/', {'title': ''})

		self.assertEqual(response.status_code, 200)
		self.assertContains(response, 'This field is required')

	def test_add_project_via_ajax_success(self):
		self.client.force_login(self.user)
		response = self.client.post(
			'/dashboard/projects/',
			{
				'title': 'AJAX Created Project',
				'description': 'Description via AJAX',
				'problem': 'Problem statement',
				'solution': 'Solution statement',
				'technologies': 'Python, Django',
				'url': 'https://example.com/ajax-proj',
				'date': '2026-09-10',
			},
			HTTP_X_REQUESTED_WITH='XMLHttpRequest',
		)
		self.assertEqual(response.status_code, 200)
		data = response.json()
		self.assertTrue(data.get('success'))
		self.assertTrue(Project.objects.filter(title='AJAX Created Project').exists())

	def test_add_project_via_ajax_error(self):
		self.client.force_login(self.user)
		response = self.client.post(
			'/dashboard/projects/',
			{'title': ''},
			HTTP_X_REQUESTED_WITH='XMLHttpRequest',
		)
		self.assertEqual(response.status_code, 400)
		data = response.json()
		self.assertFalse(data.get('success'))
		self.assertIn('errors', data)

	def test_edit_project_get_data(self):
		self.client.force_login(self.user)
		project = Project.objects.create(
			title='Original Project',
			description='Original Desc',
			problem='Original Problem',
			solution='Original Solution',
			technologies=['Python', 'Django'],
			url='https://example.com/orig',
			date='2026-09-10',
		)
		response = self.client.get(f'/dashboard/projects/{project.id}/edit/')
		self.assertEqual(response.status_code, 200)
		data = response.json()
		self.assertTrue(data.get('success'))
		self.assertEqual(data['project']['title'], 'Original Project')
		self.assertEqual(data['project']['technologies'], 'Python, Django')

	def test_edit_project_post_update(self):
		self.client.force_login(self.user)
		project = Project.objects.create(
			title='Original Title',
			description='Original Desc',
			problem='Original Problem',
			solution='Original Solution',
			technologies=['Python'],
			date='2026-09-10',
		)
		response = self.client.post(f'/dashboard/projects/{project.id}/edit/', {
			'title': 'Updated Title',
			'description': 'Updated Desc',
			'problem': 'Updated Problem',
			'solution': 'Updated Solution',
			'technologies': 'Python, FastAPI',
			'date': '2026-09-11',
		})
		self.assertRedirects(response, '/dashboard/projects/')
		project.refresh_from_db()
		self.assertEqual(project.title, 'Updated Title')
		self.assertEqual(project.technologies, ['Python', 'FastAPI'])

	def test_delete_project(self):
		self.client.force_login(self.user)
		project = Project.objects.create(
			title='Project to Delete',
			description='To be deleted',
			problem='Problem',
			solution='Solution',
			date='2026-09-10',
		)
		response = self.client.post(f'/dashboard/projects/{project.id}/delete/')
		self.assertRedirects(response, '/dashboard/projects/')
		self.assertFalse(Project.objects.filter(id=project.id).exists())


class PublicUrlTests(TestCase):
	def test_public_urls_render(self):
		for path in ('/', '/about/', '/services/', '/projects/', '/contacts/'):
			with self.subTest(path=path):
				self.assertEqual(self.client.get(path).status_code, 200)
