import string
import unittest

from Services.Link.model import generate_custom_id


class LinkIdGenerationTests(unittest.TestCase):
    def test_generate_custom_id_length_and_charset(self):
        allowed = set(string.ascii_letters + string.digits)
        short_id = generate_custom_id(10)

        self.assertEqual(len(short_id), 10)
        self.assertTrue(set(short_id).issubset(allowed))

    def test_generate_custom_id_low_collision_smoke(self):
        values = {generate_custom_id(10) for _ in range(1000)}
        self.assertEqual(len(values), 1000)


if __name__ == "__main__":
    unittest.main()
