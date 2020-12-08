from django.test import TestCase
from django.urls import reverse, resolve
from django.contrib.auth.models import User
from .models import Template
from cc.views import index, get_rep, TemplateCreateView, templates_view, get_profile
import os
import requests


class RepViewTests(TestCase):

    def test_input_bad_zip_code(self):
        response = self.client.post(reverse("cc:address"), {"zip_code": "2"})

        self.assertContains(response, f"2 is not a US zip code.")

    def test_input_good_zip_code(self):
        response = self.client.post(reverse("cc:address"), {"zip_code": "23831"})
        self.assertNotContains(response, f"23831 is not a US zip code")


class ProfileViewTests(TestCase):

    def test_cannot_add_duplicate(self):
        """Test that a profile doesn't contain duplicate officials"""
        test_user = User.objects.create_user("test", "test@example.com", "password")
        test_user.save()
        key = os.environ.get("GOOGLE_API_KEY")
        address = "23831"
        rep_info_dict = requests.get("https://www.googleapis.com/civicinfo/v2/representatives",
                                     params={"key": key, "address": address}).json()
        rep_info_dict = rep_info_dict["officials"]
        self.client.force_login(test_user)
        for rep in rep_info_dict:
            self.client.post(reverse("cc:add_rep"), content_type="application/json", data=rep)
        test_user.refresh_from_db()
        old_length = len(test_user.profile.personalList)
        for rep in rep_info_dict:
            self.client.post(reverse("cc:add_rep"), content_type="application/json", data=rep)
        test_user.refresh_from_db()
        new_length = len(test_user.profile.personalList)
        self.assertEqual(old_length, new_length)
        self.client.logout()
        User.delete(test_user)

    def test_cannot_add_un_auth(self):
        """test that a non-auth user cannot add things to a profile"""
        key = os.environ.get("GOOGLE_API_KEY")
        address = "23831"
        rep_info_dict = requests.get("https://www.googleapis.com/civicinfo/v2/representatives",
                                     params={"key": key, "address": address}).json()
        rep_info_dict = rep_info_dict["officials"]

        response = self.client.post(reverse("cc:add_rep"), content_type="application/json", data=[rep_info_dict[0]],
                                    follow=True)
        expected_url, expected_status_code = response.redirect_chain[len(response.redirect_chain) - 1]
        self.assertRedirects(response, expected_url)


class ProfileAccessTests(TestCase):
    def test_cannot_view_profile_no_login(self):
        """should redirect to login page if not logged in"""
        response = self.client.get(reverse("cc:profile"), follow=True)
        expected_url, expected_status_code = response.redirect_chain[len(response.redirect_chain) - 1]
        self.assertRedirects(response, expected_url)


class AddTemplateTest(TestCase):
    def setUp(self) -> None:
        self.user = User.objects.create_user("test", "test", "password")
        self.user.save()
        self.client.force_login(self.user)
        self.user.refresh_from_db()

    def tearDown(self) -> None:
        self.client.logout()
        User.delete(self.user)

    def test_successful_new_template_add(self):
        new_template = Template(subject="Test", body="Test")
        new_template.save()
        post_response = self.client.post(reverse("cc:add_message"), data={"pk": new_template.pk},
                                         content_type="application/json")
        self.assertEqual(post_response.status_code, 200)

    def test_add_template_twice(self):
        new_template = Template(subject="Test", body="Test")
        new_template.save()
        self.client.post(reverse("cc:add_message"), data={"pk": new_template.pk}, content_type="application/json")
        self.user.refresh_from_db()
        old_count = len(self.user.profile.templateList.all())
        self.client.post(reverse("cc:add_message"), data={"pk": new_template.pk}, content_type="application/json")
        self.user.refresh_from_db()
        new_count = len(self.user.profile.templateList.all())
        self.assertEqual(old_count, new_count)

class UrlTests(TestCase):
    def test_home(self):
        url = reverse('cc:index')
        self.assertEqual(resolve(url).func, index)
    def test_search_address(self):
        url = reverse('cc:address')
        self.assertEqual(resolve(url).func, get_rep)
    def test_submit_a_message(self):
        url = reverse('cc:submitMessage')
        self.assertEqual(resolve(url).func.view_class, TemplateCreateView)
    def test_messages(self):
        url = reverse('cc:viewMessages')
        self.assertEqual(resolve(url).func, templates_view)
    def test_profile(self):
        url = reverse('cc:profile')
        self.assertEqual(resolve(url).func, get_profile)

