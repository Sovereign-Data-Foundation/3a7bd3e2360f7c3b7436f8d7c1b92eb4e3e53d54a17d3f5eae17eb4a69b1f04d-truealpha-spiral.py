
import unittest
import os
import shutil
import sys
from tas_core.alpha.sovereign import SovereignRuntime

class TestSovereignRuntime(unittest.TestCase):
    def setUp(self):
        # Create a temp directory for testing
        self.test_dir = "test_sovereign_runtime"
        if not os.path.exists(self.test_dir):
            os.makedirs(self.test_dir)
        # Store original cwd
        self.original_cwd = os.getcwd()
        os.chdir(self.test_dir)

    def tearDown(self):
        # Return to original cwd
        os.chdir(self.original_cwd)
        # Clean up
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)

    def test_with_sovereign_gate_justification(self):
        """
        Test that with_sovereign_gate validates justification.
        """
        # Test missing justification
        with self.assertRaises(ValueError) as cm:
            SovereignRuntime.create_file("test.txt", "content")
        # Now create_file forces justification as kwarg, so failing to pass it
        # as kwarg will trigger ValueError inside the decorator if decorator runs,
        # or TypeError if python enforces signature first.
        # But decorator wraps (*args, **kwargs). So args are passed.
        # Inside wrapper: kwargs.get('justification') returns None if not passed.
        # Then ValueError is raised.
        self.assertIn("Justification must be a string", str(cm.exception))

        # Test short justification
        with self.assertRaises(ValueError) as cm:
            SovereignRuntime.create_file("test.txt", "content", justification="short")
        self.assertIn("at least 10 characters", str(cm.exception))

        # Test valid justification
        SovereignRuntime.create_file("test.txt", "content", justification="Valid justification 123")
        self.assertTrue(os.path.exists("test.txt"))

    def test_with_sovereign_gate_argument_validation(self):
        """
        Test that with_sovereign_gate rejects unsafe types.
        """
        class UnsafeObject:
            pass

        # Test passing an unsafe object as content
        unsafe_obj = UnsafeObject()
        with self.assertRaises(ValueError) as cm:
            SovereignRuntime.create_file("test.txt", unsafe_obj, justification="Valid justification 123")
        self.assertIn("Unauthorized argument type", str(cm.exception))

    def test_create_file_path_traversal(self):
        """
        Test that create_file prevents path traversal.
        """
        # Test creating file outside allowed directory (e.g., ../test.txt)
        with self.assertRaises(ValueError) as cm:
            SovereignRuntime.create_file("../traversal.txt", "content", justification="Valid justification 123")
        self.assertIn("Path traversal detected", str(cm.exception))

        # Test creating file inside allowed directory
        SovereignRuntime.create_file("safe.txt", "content", justification="Valid justification 123")
        self.assertTrue(os.path.exists("safe.txt"))

    def test_create_file_absolute_path(self):
        """
        Test that create_file prevents absolute paths if they are outside scope.
        """
        abs_path = os.path.abspath("/tmp/unsafe.txt")
        with self.assertRaises(ValueError) as cm:
            SovereignRuntime.create_file(abs_path, "content", justification="Valid justification 123")
        self.assertIn("Absolute paths are not allowed", str(cm.exception))

    def test_create_file_prefix_bypass(self):
        """
        Test that create_file prevents prefix bypass (sibling directory attack).
        e.g. if allowed is /tmp/test, prevent access to /tmp/test_secret
        """
        # Since allowed_dir is '.', and base_path is absolute path of '.',
        # creating a sibling directory requires '..' + sibling.
        # E.g. '../test_sovereign_runtime_secret'.

        # To strictly test prefix bypass, we need to mock _sanitize_path's base_path or simulate the environment.
        # But we can test effectively by trying to access a sibling directory using '..'

        with self.assertRaises(ValueError) as cm:
            SovereignRuntime.create_file(f"../{self.test_dir}_secret/exploit.txt", "content", justification="Valid justification 123")
        # This will be caught by "Path traversal detected" because commonpath will be parent dir.
        self.assertIn("Path traversal detected", str(cm.exception))

        # If sanitize_path used startswith, it might have passed if the sibling name starts with the test dir name.
        # e.g. test_dir="foo", sibling="foo_secret".
        # But since we are inside test_dir, accessing sibling requires "../foo_secret".
        # os.path.abspath("../foo_secret") -> /parent/foo_secret.
        # base_path -> /parent/foo.
        # commonpath -> /parent.
        # common != base_path. Secure.

    def test_seal_ledger_path_traversal(self):
        """
        Test that seal_ledger prevents path traversal.
        """
        with open("ledger.txt", "w") as f:
            f.write("ledger data")

        result = SovereignRuntime.seal_ledger("ledger.txt", justification="Valid justification 123")
        self.assertIn("sealed", result)

        with self.assertRaises(ValueError) as cm:
            SovereignRuntime.seal_ledger("../secret.txt", justification="Valid justification 123")
        self.assertIn("Path traversal detected", str(cm.exception))

    def test_seal_ledger_directory(self):
        """
        Test that seal_ledger rejects directories.
        """
        os.makedirs("subdir")
        with self.assertRaises(ValueError) as cm:
            SovereignRuntime.seal_ledger("subdir", justification="Valid justification 123")
        self.assertIn("Ledger must be a regular file", str(cm.exception))

    def test_justification_keyword_only(self):
        """
        Test that justification must be a keyword argument.
        """
        # Calling create_file with positional justification should fail.
        # However, the decorator intercepts (*args, **kwargs) BEFORE calling the wrapped function.
        # The decorator checks kwargs.get('justification').
        # If we pass 3 positional args: args=('test.txt', 'content', 'Positional Justification'), kwargs={}.
        # The decorator sees kwargs['justification'] is None, so it raises ValueError("Justification must be...").
        # It does NOT raise TypeError yet because it hasn't called the wrapped function.

        # So, we expect ValueError (from decorator) OR TypeError (if we bypass decorator logic or if implementation changes).
        # Given current implementation:
        with self.assertRaises((ValueError, TypeError)):
             SovereignRuntime.create_file("test.txt", "content", "Positional Justification")

if __name__ == '__main__':
    unittest.main()
