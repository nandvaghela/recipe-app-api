"""Test for models"""

from django.test import TestCase
from django.contrib.auth import get_user_model
from decimal import Decimal
from core import models

def create_user(email="user@example.com", password="password123"):
    """Helper function to create a sample user"""
    return get_user_model().objects.create_user(email, password)


class ModelTest(TestCase):
    """Test models"""

    def test_create_user_with_email_successful(self):
        """Test creating user with an email successful"""

        email = 'test@example.com'
        password = 'testpass123'
        user = get_user_model().objects.create_user(
            email=email,
            password=password
        )

        self.assertEqual(user.email, email)
        self.assertTrue(user.check_password(password))


    def test_new_user_email_normalized(self):
        """Test email is normalized for all users."""

        sample_emails=[['test1@EXAMPLE.com','test1@example.com'],
                       ['Test2@Example.com','Test2@example.com'],
                       ['TEST3@EXAMPLE.com','TEST3@example.com'],
                       ['test4@Example.com','test4@example.com'],
                       ]

        for email, expected in sample_emails:
            user = get_user_model().objects.create_user(email,'sample123')
            self.assertEqual(user.email,expected)


    def test_new_user_without_email_raises_error(self):
        """Test that new user without email raises the ValueError."""

        with self.assertRaises(ValueError):
            get_user_model().objects.create_user('','sample123')

    def test_create_superuser(self):
        """Test creating a superuser"""
        user= get_user_model().objects.create_superuser('test@example.com'
                                                        , 'test123')

        self.assertTrue(user.is_superuser)
        self.assertTrue(user.is_staff)

    def test_create_recipe(self):
        """Test creating a recipe is successful"""
        user = get_user_model().objects.create_user(
            'test@example.com',
            'pass123',
        )
        recipe = models.Recipe.objects.create(
            user = user,
            title = 'Sample Reciepe name',
            time_minutes = 5,
            price = Decimal('5.50'),
            description = 'Sample receipe description.'
        )

        self.assertEqual(str(recipe), recipe.title)

    def test_create_tag(self):
        """Test creating a tag is successful"""
        user = create_user()
        tag = models.Tag.objects.create(user=user, name='Vegan')
        self.assertEqual(str(tag), tag.name)
