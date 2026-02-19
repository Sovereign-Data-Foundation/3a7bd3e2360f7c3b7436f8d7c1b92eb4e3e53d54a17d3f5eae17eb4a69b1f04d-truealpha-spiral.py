import functools
import os
import hashlib

def with_sovereign_gate(func):
    """
    Decorator that enforces the Sovereign Gate.
    Validates the justification string AND the arguments passed to the tool.
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        # 1. Validate Justification (Standard Check)
        justification = kwargs.get('justification')
        if not justification or not isinstance(justification, str) or len(justification) < 10:
            raise ValueError("Sovereign Gate: Justification must be a string of at least 10 characters.")

        # 2. Validate Arguments (Security Fix)
        # Enforce that all arguments are safe types (str, int, float, bool, list, dict, None)
        # and that string arguments do not contain dangerous patterns if they are paths.

        # Combine args and kwargs values for checking
        all_values = list(args) + list(kwargs.values())

        for val in all_values:
            # Basic type safety check
            if val is None:
                continue
            if not isinstance(val, (str, int, float, bool, list, dict)):
                # Strictly reject unauthorized types to prevent injection of complex objects
                raise ValueError(f"Sovereign Gate: Unauthorized argument type: {type(val).__name__}. Only basic types allowed.")

        return func(*args, **kwargs)
    return wrapper

class SovereignRuntime:
    """
    Implements a secure runtime environment for agent actions.
    Enforces strict input validation and path sanitization.
    """

    @staticmethod
    def _sanitize_path(filepath, allowed_dir="."):
        """
        Sanitizes a file path to prevent traversal attacks.
        Ensures the resolved path is strictly within the allowed directory.
        """
        # Resolve the allowed directory to an absolute path
        base_path = os.path.abspath(allowed_dir)

        # Check for absolute paths
        if os.path.isabs(filepath):
            raise ValueError("Sovereign Runtime: Absolute paths are not allowed.")

        # Join the allowed directory with the provided filepath
        requested_path = os.path.abspath(os.path.join(base_path, filepath))

        # Robust check using os.path.commonpath to prevent prefix bypass (e.g. /data vs /data_secret)
        # commonpath returns the longest common sub-path.
        # If requested_path is inside base_path, the common path must be base_path.
        try:
            common = os.path.commonpath([base_path, requested_path])
        except ValueError:
            # Can happen on Windows if paths are on different drives
            raise ValueError(f"Sovereign Runtime: Path traversal detected (drive mismatch).")

        if common != base_path:
            raise ValueError(f"Sovereign Runtime: Path traversal detected. '{filepath}' is outside allowed scope.")

        return requested_path

    @staticmethod
    @with_sovereign_gate
    def create_file(filepath, content, *, justification=None):
        """
        Creates a file with the given content.
        Protected by Sovereign Gate and Path Sanitization.
        Forces justification to be a keyword-only argument.
        """
        # Validate inputs
        if not isinstance(content, str):
            raise ValueError("Content must be a string.")

        # Sanitize Path
        safe_path = SovereignRuntime._sanitize_path(filepath)

        # Write file
        try:
            with open(safe_path, 'w') as f:
                f.write(content)
        except Exception as e:
            raise RuntimeError(f"Failed to write file: {str(e)}")

        return f"File created at {filepath}"

    @staticmethod
    @with_sovereign_gate
    def seal_ledger(ledger_name, *, justification=None):
        """
        Seals a ledger by hashing its content.
        Protected by Sovereign Gate and Path Sanitization.
        Forces justification to be a keyword-only argument.
        """
        # Sanitize Path (ledger_name is treated as a file path relative to current dir)
        safe_path = SovereignRuntime._sanitize_path(ledger_name)

        if not os.path.exists(safe_path):
            raise FileNotFoundError(f"Ledger file not found: {ledger_name}")

        # Security: Ensure it's a file, not a directory or special device
        if not os.path.isfile(safe_path):
             raise ValueError(f"Ledger must be a regular file: {ledger_name}")

        # Seal (Hash)
        sha256_hash = hashlib.sha256()
        try:
            with open(safe_path, "rb") as f:
                for byte_block in iter(lambda: f.read(4096), b""):
                    sha256_hash.update(byte_block)
        except Exception as e:
             raise RuntimeError(f"Failed to read ledger: {str(e)}")

        return f"Ledger {ledger_name} sealed. Hash: {sha256_hash.hexdigest()}"
