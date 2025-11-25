from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from rest_framework import status
from rest_framework.test import APITestCase

from materials.models import Lesson, Subscription, Course

User = get_user_model()


class MaterialsTestCase(APITestCase):

    def setUp(self) -> None:
        # создаём пользователя
        self.user = User.objects.create_user(
            email='testuser@test.com',
            password='testpass123',
            username='testuser'
        )

        # создаём группу модераторов и добавляем пользователя в неё
        self.moderator_group, _ = Group.objects.get_or_create(name="moderator")
        self.user.groups.add(self.moderator_group)

        # логинимся
        self.client.force_authenticate(user=self.user)

        # создаём курс
        self.course = Course.objects.create(
            title='Test course 1',
            description='Test course descr 1',
            owner=self.user
        )

        # создаём несколько уроков
        self.lesson1 = Lesson.objects.create(
            title='Lesson 1',
            description='Descr 1',
            link='https://youtu.be/111',
            course=self.course,
            owner=self.user
        )
        self.lesson2 = Lesson.objects.create(
            title='Lesson 2',
            description='Descr 2',
            link='https://youtu.be/222',
            course=self.course,
            owner=self.user
        )


    def test_create_lesson(self):
        """ Тестирование создания уроков """

        data = {
            'title': 'Test lesson 1',
            'description': 'Test descr 1',
            'link': 'https://www.youtube.com/watch?v=CIbnDLv7sys&t',
            'course': self.course.id,  # существующий id
            # 'owner' не передаём!
        }

        response = self.client.post(
            '/lessons/create/',
            data=data
        )

        print(response.status_code, response.json())

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED
        )

        # пример адекватной проверки ответа
        self.assertEqual(
            response.json()['title'],
            'Test lesson 1'
        )
        self.assertEqual(
            response.json()['course'],
            self.course.id
        )
        self.assertEqual(
            response.json()['owner'],
            self.user.id
        )

        self.assertTrue(
            Lesson.objects.filter(title='Test lesson 1').exists()
        )

    def test_list_lessons(self):
        """ Тестирование вывода списка уроков """

        response = self.client.get('/lessons/')

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        json_data = response.json()

        # Пагинация MaterialsPaginator(page_size=2)
        self.assertIn('count', json_data)
        self.assertIn('results', json_data)

        self.assertEqual(json_data['count'], 2)  # всего уроков
        self.assertEqual(len(json_data['results']), 2)  # оба попали на первую страницу

        titles = [lesson['title'] for lesson in json_data['results']]
        self.assertEqual(titles, ['Lesson 1', 'Lesson 2'])

    def test_update_lesson(self):
        """ Тестирование обновления урока """

        data = {
            'title': 'Updated lesson title',
            'description': 'Updated descr',
            'link': 'https://youtu.be/updated',
            'course': self.course.id,
        }

        response = self.client.put(
            f'/lessons/update/{self.lesson1.id}/',
            data=data
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        updated = Lesson.objects.get(id=self.lesson1.id)

        self.assertEqual(updated.title, 'Updated lesson title')
        self.assertEqual(updated.description, 'Updated descr')
        self.assertEqual(updated.link, 'https://youtu.be/updated')

    def test_delete_lesson(self):
        """ Тестирование удаления урока """

        response = self.client.delete(
            f'/lessons/delete/{self.lesson2.id}/'
        )

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        self.assertFalse(
            Lesson.objects.filter(id=self.lesson2.id).exists()
        )


    def test_create_subscription(self):
        """Тестирование создания подписки на курс"""

        # на стартe подписки нет
        self.assertFalse(
            Subscription.objects.filter(user=self.user, course=self.course).exists()
        )

        response = self.client.post(
            '/subscriptions/',
            data={'course_id': self.course.id}
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json(), {'message': 'подписка добавлена'})

        # подписка появилась
        self.assertTrue(
            Subscription.objects.filter(user=self.user, course=self.course).exists()
        )

    def test_delete_subscription(self):
        """Тестирование удаления существующей подписки"""

        # заранее создаём подписку
        Subscription.objects.create(
            user=self.user,
            course=self.course,
            title=f"Подписка на курс {self.course.title}",
        )

        self.assertTrue(
            Subscription.objects.filter(user=self.user, course=self.course).exists()
        )

        response = self.client.post(
            '/subscriptions/',
            data={'course_id': self.course.id}
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json(), {'message': 'подписка удалена'})

        # подписка удалена
        self.assertFalse(
            Subscription.objects.filter(user=self.user, course=self.course).exists()
        )

