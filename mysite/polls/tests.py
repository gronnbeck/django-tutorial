import datetime

from django.test import TestCase
from django.utils import timezone
from django.urls import reverse

from .models import Question

def create_question(question_text, days):
    time = timezone.now() + datetime.timedelta(days=days)
    return Question.objects.create(question_text=question_text, pub_date=time)

def create_past_question(text="Past question."):
    return create_question(question_text=text, days=-30)

def create_future_question():
    return create_question(question_text="Future question.", days=30)

class QuestionModelTests(TestCase):

    def test_was_published_recently_with_future_questions(self):
        future_question = create_future_question()
        self.assert_is_not_recently_published(future_question)

    def test_was_published_recently_with_old_questions(self):
        old_question = create_past_question()
        self.assert_is_not_recently_published(old_question)

    def test_was_published_recently_with_recent_question(self):
        recent_question = create_question("recent", 0)
        self.assert_is_recently_published(recent_question)

    def assert_is_not_recently_published(self, question):
        self.assertIs(question.was_published_recently(), False)

    def assert_is_recently_published(self, question):
        self.assertIs(question.was_published_recently(), True)

class QuestionIndexViewTests(TestCase):
    def test_no_question(self):
        response = self.get_polls_index()
        self.assert_no_polls_available(response)

    def test_past_question(self):
        create_past_question()
        response = self.get_polls_index()
        self.assert_query_set_contains_only_past_question(response)

    def test_future_question(self):
        create_future_question()
        response = self.get_polls_index()
        self.assertQuerysetEqual(
            response.context['latest_question_list'], [])

    def test_past_and_future_question(self):
        create_past_question()
        create_future_question()
        response = self.get_polls_index()
        self.assert_query_set_contains_only_past_question(response)

    def test_two_past_questions(self):
        create_past_question(text="Past question 1.")
        create_past_question(text="Past question 2.")
        response = self.get_polls_index()
        self.assertQuerysetEqual(
            response.context['latest_question_list'],
            ['<Question: Past question 2.>', '<Question: Past question 1.>']
        )

    def get_polls_index(self):
        return self.client.get(reverse('polls:index'))

    def assert_no_polls_available(self, response):
        self.assertEquals(response.status_code, 200)
        self.assertContains(response, "No polls are available.")
        self.assertQuerysetEqual(response.context['latest_question_list'], [])

    def assert_query_set_contains_only_past_question(self, response):
        self.assertQuerysetEqual(
            response.context['latest_question_list'],
            ['<Question: Past question.>']
        )

class QuestionDetailViewTests(TestCase):
    def test_future_question(self):
        future_question = create_future_question()
        url = reverse('polls:detail', args=(future_question.id,))
        response = self.client.get(url)
        self.assertEquals(response.status_code, 404)

    def test_past_question(self):
        past_question = create_past_question()
        url = reverse('polls:detail', args=(past_question.id,))
        response = self.client.get(url)
        self.assertContains(response, past_question.question_text)


