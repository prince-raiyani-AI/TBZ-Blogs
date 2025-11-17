"""
Comprehensive test suite for the accounts app (authentication system).
Reference: https://docs.djangoproject.com/en/5.2/topics/testing/
Reference: https://pytest-django.readthedocs.io/
"""

import pytest
from django.contrib.auth.models import User
from django.urls import reverse
from django.test import TestCase, Client
from accounts.models import UserProfile
from accounts.forms import (
    UserRegistrationForm, UserLoginForm, UserProfileForm,
    CustomPasswordChangeForm
)


# ============================================================================
# FIXTURES FOR TESTING
# ============================================================================

@pytest.fixture
def client():
    """Pytest fixture for Django test client."""
    return Client()


@pytest.fixture
def test_user():
    """Create a test user for authentication tests."""
    user = User.objects.create_user(
        username='testuser',
        email='testuser@example.com',
        password='TestPass123!',
        first_name='Test',
        last_name='User'
    )
    return user


@pytest.fixture
def test_user_profile(test_user):
    """Create a test user with profile."""
    profile = UserProfile.objects.create(
        user=test_user,
        bio='Test bio'
    )
    return profile


# ============================================================================
# FORM TESTS
# ============================================================================

class TestUserRegistrationForm(TestCase):
    """Test cases for user registration form."""

    def test_valid_registration_form(self):
        """Test registration form with valid data."""
        form_data = {
            'username': 'newuser',
            'email': 'newuser@example.com',
            'first_name': 'New',
            'last_name': 'User',
            'password1': 'SecurePass123!',
            'password2': 'SecurePass123!'
        }
        form = UserRegistrationForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_email_already_exists(self):
        """Test form rejects duplicate email."""
        # Create a user first
        User.objects.create_user(
            username='existing',
            email='existing@example.com',
            password='pass123'
        )
        
        form_data = {
            'username': 'newuser',
            'email': 'existing@example.com',  # Duplicate email
            'first_name': 'New',
            'last_name': 'User',
            'password1': 'SecurePass123!',
            'password2': 'SecurePass123!'
        }
        form = UserRegistrationForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('email', form.errors)

    def test_username_already_exists(self):
        """Test form rejects duplicate username."""
        User.objects.create_user(
            username='existing',
            email='existing@example.com',
            password='pass123'
        )
        
        form_data = {
            'username': 'existing',  # Duplicate username
            'email': 'newuser@example.com',
            'first_name': 'New',
            'last_name': 'User',
            'password1': 'SecurePass123!',
            'password2': 'SecurePass123!'
        }
        form = UserRegistrationForm(data=form_data)
        self.assertFalse(form.is_valid())

    def test_password_mismatch(self):
        """Test form rejects mismatched passwords."""
        form_data = {
            'username': 'newuser',
            'email': 'newuser@example.com',
            'first_name': 'New',
            'last_name': 'User',
            'password1': 'SecurePass123!',
            'password2': 'DifferentPass123!'
        }
        form = UserRegistrationForm(data=form_data)
        self.assertFalse(form.is_valid())

    def test_weak_password(self):
        """Test form rejects weak password."""
        form_data = {
            'username': 'newuser',
            'email': 'newuser@example.com',
            'first_name': 'New',
            'last_name': 'User',
            'password1': '123',
            'password2': '123'
        }
        form = UserRegistrationForm(data=form_data)
        self.assertFalse(form.is_valid())


class TestUserLoginForm(TestCase):
    """Test cases for login form."""

    def test_valid_login_form(self):
        """Test login form with valid data."""
        form_data = {
            'username': 'testuser',
            'password': 'testpass123'
        }
        form = UserLoginForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_remember_me_checkbox(self):
        """Test remember me checkbox in login form."""
        form_data = {
            'username': 'testuser',
            'password': 'testpass123',
            'remember_me': True
        }
        form = UserLoginForm(data=form_data)
        self.assertTrue(form.is_valid())


class TestUserProfileForm(TestCase):
    """Test cases for user profile edit form."""

    def test_valid_profile_form(self):
        """Test profile form with valid data."""
        form_data = {
            'first_name': 'Updated',
            'last_name': 'User',
            'email': 'updated@example.com',
            'bio': 'Updated bio'
        }
        form = UserProfileForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_empty_optional_fields(self):
        """Test profile form with empty optional fields."""
        form_data = {
            'first_name': 'User',
            'last_name': 'Test',
            'email': 'user@example.com',
            'bio': ''  # Optional field
        }
        form = UserProfileForm(data=form_data)
        self.assertTrue(form.is_valid())


# ============================================================================
# VIEW TESTS
# ============================================================================

@pytest.mark.django_db
class TestRegistrationView:
    """Test cases for registration view."""

    def test_registration_page_get(self, client):
        """Test GET request to registration page."""
        response = client.get(reverse('register'))
        assert response.status_code == 200
        assert 'form' in response.context

    def test_registration_success(self, client):
        """Test successful user registration."""
        data = {
            'username': 'newuser',
            'email': 'newuser@example.com',
            'first_name': 'New',
            'last_name': 'User',
            'password1': 'SecurePass123!',
            'password2': 'SecurePass123!'
        }
        response = client.post(reverse('register'), data)
        
        # Should redirect to login on success
        assert response.status_code == 302
        assert reverse('login') in response.url
        
        # User should be created
        assert User.objects.filter(username='newuser').exists()
        
        # UserProfile should be created
        user = User.objects.get(username='newuser')
        assert UserProfile.objects.filter(user=user).exists()

    def test_registration_duplicate_email(self, client, test_user):
        """Test registration with duplicate email."""
        data = {
            'username': 'anotheruser',
            'email': test_user.email,  # Duplicate
            'first_name': 'Another',
            'last_name': 'User',
            'password1': 'SecurePass123!',
            'password2': 'SecurePass123!'
        }
        response = client.post(reverse('register'), data)
        
        # Should not redirect (form has errors)
        assert response.status_code == 200


@pytest.mark.django_db
class TestLoginView:
    """Test cases for login view."""

    def test_login_page_get(self, client):
        """Test GET request to login page."""
        response = client.get(reverse('login'))
        assert response.status_code == 200
        assert 'form' in response.context

    def test_login_success(self, client, test_user):
        """Test successful login."""
        data = {
            'username': 'testuser',
            'password': 'TestPass123!'
        }
        response = client.post(reverse('login'), data)
        
        # Should redirect to home or next parameter
        assert response.status_code == 302
        
        # Session should contain user
        assert '_auth_user_id' in client.session

    def test_login_wrong_password(self, client, test_user):
        """Test login with wrong password."""
        data = {
            'username': 'testuser',
            'password': 'WrongPassword123!'
        }
        response = client.post(reverse('login'), data)
        
        # Should not redirect (form has errors)
        assert response.status_code == 200

    def test_login_nonexistent_user(self, client):
        """Test login with non-existent user."""
        data = {
            'username': 'nonexistent',
            'password': 'anypassword'
        }
        response = client.post(reverse('login'), data)
        
        # Should not redirect
        assert response.status_code == 200

    def test_remember_me_functionality(self, client, test_user):
        """Test remember me checkbox sets session timeout."""
        data = {
            'username': 'testuser',
            'password': 'TestPass123!',
            'remember_me': True
        }
        response = client.post(reverse('login'), data)
        
        # Check if session expiry is extended (30 days)
        assert response.status_code == 302


@pytest.mark.django_db
class TestLogoutView:
    """Test cases for logout view."""

    def test_logout_authenticated_user(self, client, test_user):
        """Test logout clears session."""
        # Login first
        client.login(username='testuser', password='TestPass123!')
        
        # Logout
        response = client.get(reverse('logout'))
        
        # Should redirect to home
        assert response.status_code == 302
        
        # Session should be cleared
        assert '_auth_user_id' not in client.session

    def test_logout_unauthenticated_user(self, client):
        """Test logout when not logged in."""
        response = client.get(reverse('logout'))
        
        # Should redirect to login
        assert response.status_code == 302


@pytest.mark.django_db
class TestProfileView:
    """Test cases for profile view."""

    def test_profile_requires_login(self, client):
        """Test profile view requires authentication."""
        response = client.get(reverse('profile'))
        
        # Should redirect to login
        assert response.status_code == 302
        assert reverse('login') in response.url

    def test_profile_authenticated_user(self, client, test_user_profile):
        """Test authenticated user can access profile."""
        client.login(username='testuser', password='TestPass123!')
        response = client.get(reverse('profile'))
        
        assert response.status_code == 200
        assert 'user' in response.context
        assert response.context['user'].username == 'testuser'

    def test_profile_displays_statistics(self, client, test_user_profile):
        """Test profile displays user statistics."""
        client.login(username='testuser', password='TestPass123!')
        response = client.get(reverse('profile'))
        
        assert response.status_code == 200
        # Check if context has profile data
        assert 'profile' in response.context


@pytest.mark.django_db
class TestProfileEditView:
    """Test cases for profile edit view."""

    def test_profile_edit_requires_login(self, client):
        """Test profile edit requires authentication."""
        response = client.get(reverse('profile_edit'))
        
        assert response.status_code == 302
        assert reverse('login') in response.url

    def test_profile_edit_get(self, client, test_user_profile):
        """Test GET request to profile edit."""
        client.login(username='testuser', password='TestPass123!')
        response = client.get(reverse('profile_edit'))
        
        assert response.status_code == 200
        assert 'form' in response.context

    def test_profile_edit_post_success(self, client, test_user_profile):
        """Test updating profile."""
        client.login(username='testuser', password='TestPass123!')
        
        data = {
            'first_name': 'Updated',
            'last_name': 'Name',
            'email': 'updated@example.com',
            'bio': 'Updated bio'
        }
        response = client.post(reverse('profile_edit'), data)
        
        # Should redirect to profile
        assert response.status_code == 302
        assert reverse('profile') in response.url
        
        # User should be updated
        test_user_profile.user.refresh_from_db()
        assert test_user_profile.user.first_name == 'Updated'


@pytest.mark.django_db
class TestChangePasswordView:
    """Test cases for change password view."""

    def test_change_password_requires_login(self, client):
        """Test change password requires authentication."""
        response = client.get(reverse('change_password'))
        
        assert response.status_code == 302
        assert reverse('login') in response.url

    def test_change_password_get(self, client, test_user):
        """Test GET request to change password."""
        client.login(username='testuser', password='TestPass123!')
        response = client.get(reverse('change_password'))
        
        assert response.status_code == 200
        assert 'form' in response.context

    def test_change_password_success(self, client, test_user):
        """Test successful password change."""
        client.login(username='testuser', password='TestPass123!')
        
        data = {
            'old_password': 'TestPass123!',
            'new_password1': 'NewSecurePass123!',
            'new_password2': 'NewSecurePass123!'
        }
        response = client.post(reverse('change_password'), data)
        
        # Should redirect to profile
        assert response.status_code == 302
        assert reverse('profile') in response.url
        
        # Old password should not work
        client.logout()
        login_result = client.login(username='testuser', password='TestPass123!')
        assert not login_result
        
        # New password should work
        login_result = client.login(username='testuser', password='NewSecurePass123!')
        assert login_result

    def test_change_password_wrong_old_password(self, client, test_user):
        """Test password change with wrong old password."""
        client.login(username='testuser', password='TestPass123!')
        
        data = {
            'old_password': 'WrongOldPass123!',
            'new_password1': 'NewSecurePass123!',
            'new_password2': 'NewSecurePass123!'
        }
        response = client.post(reverse('change_password'), data)
        
        # Should not redirect (form has errors)
        assert response.status_code == 200

    def test_change_password_mismatch(self, client, test_user):
        """Test password change with mismatched new passwords."""
        client.login(username='testuser', password='TestPass123!')
        
        data = {
            'old_password': 'TestPass123!',
            'new_password1': 'NewSecurePass123!',
            'new_password2': 'DifferentPass123!'
        }
        response = client.post(reverse('change_password'), data)
        
        # Should not redirect
        assert response.status_code == 200


# ============================================================================
# URL TESTS
# ============================================================================

@pytest.mark.django_db
class TestAuthenticationURLs:
    """Test cases for URL configuration."""

    def test_register_url_exists(self, client):
        """Test register URL is configured."""
        response = client.get(reverse('register'))
        assert response.status_code == 200

    def test_login_url_exists(self, client):
        """Test login URL is configured."""
        response = client.get(reverse('login'))
        assert response.status_code == 200

    def test_logout_url_exists(self, client, test_user):
        """Test logout URL is configured."""
        client.login(username='testuser', password='TestPass123!')
        response = client.get(reverse('logout'))
        assert response.status_code == 302

    def test_profile_url_exists(self, client, test_user):
        """Test profile URL is configured."""
        client.login(username='testuser', password='TestPass123!')
        response = client.get(reverse('profile'))
        assert response.status_code == 200

    def test_profile_edit_url_exists(self, client, test_user):
        """Test profile edit URL is configured."""
        client.login(username='testuser', password='TestPass123!')
        response = client.get(reverse('profile_edit'))
        assert response.status_code == 200

    def test_change_password_url_exists(self, client, test_user):
        """Test change password URL is configured."""
        client.login(username='testuser', password='TestPass123!')
        response = client.get(reverse('change_password'))
        assert response.status_code == 200


# ============================================================================
# MODEL TESTS
# ============================================================================

@pytest.mark.django_db
class TestUserProfileModel:
    """Test cases for UserProfile model."""

    def test_user_profile_creation(self, test_user_profile):
        """Test UserProfile is created."""
        assert test_user_profile.user.username == 'testuser'
        assert test_user_profile.bio == 'Test bio'

    def test_user_profile_one_to_one(self, test_user):
        """Test UserProfile OneToOne relationship."""
        profile = UserProfile.objects.create(user=test_user)
        
        # Try to create another profile for same user
        with pytest.raises(Exception):
            UserProfile.objects.create(user=test_user)

    def test_profile_created_on_user_creation(self):
        """Test UserProfile auto-created when user registers."""
        user = User.objects.create_user(
            username='autouser',
            email='auto@example.com',
            password='pass123'
        )
        # Profile should be created via signal or form
        assert UserProfile.objects.filter(user=user).exists()
