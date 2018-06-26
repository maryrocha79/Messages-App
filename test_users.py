from app import app, User
import unittest


class MyAppTestCase(unittest.TestCase):
    def test_users_index(self):
        client = app.test_client()

        result = client.get('/users')
        self.assertIn(b'Users List', result.data)

    def test_add_user(self):
        client = app.test_client()
        result = client.post(
            '/users',
            data={
                'first_name': 'Juan',
                'last_name': 'Rocha',
                'image': ''
            })

        juan = User.query.filter(User.first_name == "Juan",
                                 User.last_name == "Rocha").first()

        self.assertEqual(juan.first_name, "Juan")

        result = client.get("/users")
        self.assertIn(b'Juan Rocha', result.data)

        # self.assertIn(, result.data)

    def test_show_user(self):
        client = app.test_client()
        result = client.get('/users/2')
        self.assertIn(b'Mateo valbuena', result.data)

    def test_edit_user(self):
        client = app.test_client()
        result = client.patch(
            '/users/5',
            data={
                'first_name': 'Stella',
                'last_name': 'Wilches',
                'image': ''
            })
        stella = User.query.filter(User.first_name == "Stella",
                                   User.last_name == "Wilches").one()
        self.assertEqual(stella.first_name, "Stella")

    def test_delete_user(self):
        client = app.test_client()
        result = client.delete('/users/20')
        juan2 = User.query.filter(User.id == 20).first()
        self.assertEqual(juan2, None)

    def test_wrong_url(self):
        client = app.test_client()
        result = client.get('/users/1909/edit')
        self.assertEqual(result.status_code, 404)


if __name__ == '__main__':
    unittest.main()
