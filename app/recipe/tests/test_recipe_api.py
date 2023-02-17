"""Test for recipe API"""

import tempfile
import os

from PIL import Image
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from decimal import Decimal
from rest_framework import status
from rest_framework.test import APIClient
from core.models import Recipe, Tag, Ingredient
from recipe.serializers import (RecipeSerializer,
                                RecipeDetailSerializer,)


RECIPE_URL = reverse('recipe:recipe-list')


def detail_url(recipe_id):
    """Return recipe detail URL"""
    return reverse('recipe:recipe-detail', args=[recipe_id])


def image_upload_url(recipe_id):
    """Return URL for recipe image upload"""
    return reverse('recipe:recipe-upload-image', args=[recipe_id])

def create_recipe(user, **params):
    """Helper function to create a sample recipe"""
    defaults = {
        'title': 'Sample recipe',
        'time_minutes': 10,
        'price': Decimal('7.00'),
        'description': 'Sample description',
        'link': 'https://www.examplerecipe.com',
    }
    defaults.update(params)

    recipe = Recipe.objects.create(user=user, **defaults)
    return recipe

def create_user(**params):
    """Helper function to create a sample user"""
    return get_user_model().objects.create_user(**params)


class PublicRecipeApiTests(TestCase):
    """Test unauthenticated recipe API access"""

    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        """Test that authentication is required"""
        res = self.client.get(RECIPE_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateRecipeApiTests(TestCase):
    """Test authenticated recipe API access"""

    def setUp(self):
        self.client = APIClient()
        self.user = create_user(email = 'user@example.com', password = 'password123')
        self.client.force_authenticate(self.user)

    def test_retrieve_recipes(self):
        """Test retrieving a list of recipes"""
        create_recipe(user = self.user)
        create_recipe(user = self.user)

        res = self.client.get(RECIPE_URL)

        recipes = Recipe.objects.all().order_by('-id')
        serializer = RecipeSerializer(recipes, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)


    def test_recipes_limited_to_user(self):
        """Test retrieving recipes for user"""
        user2 = create_user(
            email = 'user2@example.com',
            password = 'password123',
        )
        create_recipe(user = user2)
        create_recipe(user = self.user)

        res = self.client.get(RECIPE_URL)
        recipes = Recipe.objects.filter(user=self.user)
        serializer = RecipeSerializer(recipes, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_view_recipe_detail(self):
        """Test viewing a recipe detail"""
        recipe = create_recipe(user = self.user)

        url = detail_url(recipe.id)
        res = self.client.get(url)

        serializer = RecipeDetailSerializer(recipe)
        self.assertEqual(res.data, serializer.data)

    def test_create_recipe(self):
        """Test creating recipe"""
        payload = {
            'title': 'Cheese cake',
            'time_minutes': 45,
            'price': Decimal('12.00'),
            'description': 'Sample description',
            'link': 'https://www.examplerecipe.com',
        }
        res = self.client.post(RECIPE_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        recipe = Recipe.objects.get(id=res.data['id'])
        for k, v in payload.items():
            self.assertEqual(getattr(recipe, k), v)
        self.assertEqual(recipe.user, self.user)

    def test_partial_update_recipe(self):
        """Test updating a recipe with patch"""
        original_link = 'https://www.examplerecipe.com'
        recipe = create_recipe(user = self.user,
                               title= 'Sample Recipe Title',
                                 link = original_link)


        payload = {'title': 'New title'}
        url = detail_url(recipe.id)
        res = self.client.patch(url, payload)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        recipe.refresh_from_db()
        self.assertEqual(recipe.title, payload['title'])
        self.assertEqual(recipe.link, original_link)
        self.assertEqual(recipe.user, self.user)


    def test_full_update_recipe(self):
        """"Test updating a recipe with put"""
        original_link = 'https://www.examplerecipe.com'
        recipe = create_recipe(user = self.user,
                               title= 'Sample Recipe Title',
                                 link = original_link,
                               description = 'Sample description',)

        payload = {
            'title': 'New title',
            'time_minutes': 49,
            'price': Decimal('12.00'),
            'description': 'Sample description',
            'link': 'https://www.examplerecipe.com',
        }
        url = detail_url(recipe.id)
        res = self.client.put(url, payload)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        recipe.refresh_from_db()
        for k, v in payload.items():
            self.assertEqual(getattr(recipe, k), v)
        self.assertEqual(recipe.user, self.user)


    def test_update_user_returns_error(self):
        """Test that updating the user returns an error"""
        new_user = create_user(
            email='user2@example.com',
            password='password123',
        )
        recipe = create_recipe(user = self.user)
        payload = {'user': new_user.id}
        url = detail_url(recipe.id)
        res = self.client.patch(url, payload)
        recipe.refresh_from_db()

        self.assertEqual(recipe.user, self.user)

    def test_delete_recipe(self):
        """Test deleting a recipe"""
        recipe = create_recipe(user = self.user)
        url = detail_url(recipe.id)
        res = self.client.delete(url)

        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Recipe.objects.filter(id=recipe.id).exists())

    def test_other_users_recipe_error(self):
        """Test that other users recipes are not returned"""
        user2 = create_user(
            email='user2@example.com',
            password='password123',
        )
        recipe = create_recipe(user = user2)
        url = detail_url(recipe.id)
        res = self.client.delete(url)

        self.assertEqual(res.status_code, status.HTTP_404_NOT_FOUND)
        self.assertTrue(Recipe.objects.filter(id=recipe.id).exists())

    def test_create_recipe_with_tags(self):
        """Test creating a recipe with tags"""

        payload = {
            'title': 'Italian Pizza',
            'tags': [{'name': 'Italian'}, {'name': 'Pizza'}],
            'time_minutes': 60,
            'price': Decimal('20.00'),
            'description': 'Sample description',
            'link': 'https://www.examplerecipe.com',
        }
        res = self.client.post(RECIPE_URL, payload, format='json')
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        recipes = Recipe.objects.filter(user=self.user)
        self.assertEqual(recipes.count(), 1)
        recipe = recipes[0]

        self.assertEqual(recipe.tags.count(), 2)
        for tag in payload['tags']:
            exists = recipe.tags.filter(
                name=tag['name'],
                user = self.user
            ).exists()
            self.assertTrue(exists)


    def test_create_recipe_with_existing_tag(self):
        """Test creating a recipe with an existing tag"""
        tag_indian = Tag.objects.create(user = self.user, name='Indian')
        payload = {
            'title': 'Masala Dosa',
            'time_minutes': 60,
            'price': Decimal('15.00'),
            'description': 'Sample Dosa description',
            'link': 'https://www.examplerecipe.com',
            'tags': [{'name': 'Indian'}, {'name': 'Dosa'}]
        }
        res = self.client.post(RECIPE_URL, payload, format='json')
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        recipes = Recipe.objects.filter(user=self.user)
        self.assertEqual(recipes.count(), 1)
        recipe = recipes[0]

        self.assertEqual(recipe.tags.count(), 2)
        self.assertIn(tag_indian, recipe.tags.all())
        for tag in payload['tags']:
            exists = recipe.tags.filter(
                name=tag['name'],
                user = self.user
            ).exists()
            self.assertTrue(exists)

    def test_create_tag_on_update(self):
        """Test creating a tag on update"""
        recipe = create_recipe(user = self.user)
        payload = {
            'tags': [{'name': 'Indian'}, {'name': 'Dosa'}]
        }
        url = detail_url(recipe.id)
        res = self.client.patch(url, payload, format='json')
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        new_tag = Tag.objects.get(user=self.user, name='Indian')
        self.assertIn(new_tag, recipe.tags.all())

    def test_update_recipe_assign_tag(self):
        """Test updating a recipe with a tag"""
        recipe = create_recipe(user = self.user)
        tag_breakfast = Tag.objects.create(user = self.user, name='Breakfast')
        recipe.tags.add(tag_breakfast)
        tag_lunch = Tag.objects.create(user = self.user, name='Lunch')
        payload = {
            'tags': [{'name': 'Lunch'}],
        }
        url = detail_url(recipe.id)
        res = self.client.patch(url, payload, format='json')
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn(tag_lunch, recipe.tags.all())
        self.assertNotIn(tag_breakfast, recipe.tags.all())

    def test_cleat_recipe_tags(self):
        """Test clearing tags from a recipe"""
        recipe = create_recipe(user = self.user)
        tag_breakfast = Tag.objects.create(user = self.user, name='Breakfast')
        recipe.tags.add(tag_breakfast)
        payload = {
            'tags': [],
        }
        url = detail_url(recipe.id)
        res = self.client.patch(url, payload, format='json')
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(recipe.tags.count(), 0)

    def test_create_new_recipe_with_ingredients(self):
        """Test creating a recipe with ingredients"""
        payload = {
            'title': 'Butter Chicken',
            'ingredients': [{'name': 'Chicken'}, {'name': 'Indian'}],
            'time_minutes': 60,
            'price': Decimal('23.00'),
            'description': 'Sample description',
            'link': 'https://www.examplerecipe.com',
        }
        res = self.client.post(RECIPE_URL, payload, format='json')
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        recipes = Recipe.objects.filter(user=self.user)
        self.assertEqual(recipes.count(), 1)
        recipe = recipes[0]

        self.assertEqual(recipe.ingredients.count(), 2)
        for ingredient in payload['ingredients']:
            exists = recipe.ingredients.filter(
                name=ingredient['name'],
                user = self.user
            ).exists()
            self.assertTrue(exists)

    def test_create_recipe_with_existing_ingredient(self):
        """Test creating a recipe with an existing ingredient"""
        ingredient_chicken = Ingredient.objects.create(user = self.user, name='Chicken')
        payload = {
            'title': 'Butter Chicken',
            'time_minutes': 60,
            'price': Decimal('23.00'),
            'description': 'Sample description',
            'link': 'https://www.examplerecipe.com',
            'ingredients': [{'name': 'Chicken'}, {'name': 'Indian'}]
        }
        res = self.client.post(RECIPE_URL, payload, format='json')
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        recipes = Recipe.objects.filter(user=self.user)
        self.assertEqual(recipes.count(), 1)
        recipe = recipes[0]

        self.assertEqual(recipe.ingredients.count(), 2)
        self.assertIn(ingredient_chicken, recipe.ingredients.all())
        for ingredient in payload['ingredients']:
            exists = recipe.ingredients.filter(
                name=ingredient['name'],
                user = self.user
            ).exists()
            self.assertTrue(exists)

    def test_create_ingredient_on_update(self):
        """Test creating an ingredient on update"""
        recipe = create_recipe(user = self.user)
        payload = {
            'ingredients': [{'name': 'Samosa'}, {'name': 'Indian'}]
        }
        url = detail_url(recipe.id)
        res = self.client.patch(url, payload, format='json')
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        new_ingredient = Ingredient.objects.get(user=self.user, name='Samosa')
        self.assertIn(new_ingredient, recipe.ingredients.all())

    def test_update_recipe_assign_ingredient(self):
        """Test updating a recipe with an ingredient"""
        recipe = create_recipe(user = self.user)
        ingredient_chicken = Ingredient.objects.create(user = self.user, name='Chicken')
        recipe.ingredients.add(ingredient_chicken)
        ingredient_samosa = Ingredient.objects.create(user = self.user, name='Samosa')
        payload = {
            'ingredients': [{'name': 'Samosa'}],
        }
        url = detail_url(recipe.id)
        res = self.client.patch(url, payload, format='json')
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn(ingredient_samosa, recipe.ingredients.all())
        self.assertNotIn(ingredient_chicken, recipe.ingredients.all())

    def test_cleat_recipe_ingredients(self):
        """Test clearing ingredients from a recipe"""
        recipe = create_recipe(user = self.user)
        ingredient_onion = Ingredient.objects.create(user = self.user, name='Onion')
        recipe.ingredients.add(ingredient_onion)
        payload = {
            'ingredients': [],
        }
        url = detail_url(recipe.id)
        res = self.client.patch(url, payload, format='json')
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(recipe.ingredients.count(), 0)


class ImageUploadTests(TestCase):
    """Test for uploading images to recipes"""

    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
                'user@example.com','password123')
        self.client.force_authenticate(self.user)
        self.recipe = create_recipe(user = self.user)

    def tearDown(self):
        self.recipe.image.delete()

    def test_upload_image(self):
        """Test uploading an image to a recipe"""
        url = image_upload_url(self.recipe.id)
        with tempfile.NamedTemporaryFile(suffix='.jpg') as image_file:
            img = Image.new('RGB', (10, 10))
            img.save(image_file, format='JPEG')
            image_file.seek(0)
            payload = {'image': image_file}
            res = self.client.post(url, payload, format='multipart')

        self.recipe.refresh_from_db()
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn('image', res.data)
        self.assertTrue(os.path.exists(self.recipe.image.path))

    def test_upload_image_bad_request(self):
        """Test uploading an invalid image"""
        url = image_upload_url(self.recipe.id)
        payload = {'image': 'notanimage'}
        res = self.client.post(url, payload, format='multipart')
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
