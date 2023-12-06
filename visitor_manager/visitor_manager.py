import json
import os
from logger.decorators import logging_decorator

from parsers.python_parser import PythonParser
from models.models import ModuleModel

EXCLUDED_DIRECTORIES: set[str] = {".venv", "node_modules", "__pycache__", ".git"}


class VisitorManager:
    """Manages the visiting and processing of Python files in a given directory.

    This class scans a specified directory, filters for Python files, parses them, and saves the parsed data in a structured JSON format. It also maintains a mapping of directories to the Python files they contain.

    Attributes:
        directory (str): The root directory to scan for Python files.
        output_directory (str): The directory where output JSON files will be saved.
        directory_modules (dict): A mapping of directories to their contained Python files.

    Example:
        >>> vm = VisitorManager("/path/to/python/code", "output")
        >>> vm.process_files()
        # This will process all Python files in /path/to/python/code and save their parsed data in the output directory.

        # If you want to save a mapping of directories to Python files, you can call the save_visited_directories method.
        >>> vm.save_visited_directories()
    """

    @logging_decorator(message="Initializing VisitorManager")
    def __init__(self, directory: str, output_directory: str = "output") -> None:
        self.directory: str = directory
        self.output_directory: str = output_directory
        self._create_output_directory()
        self.directory_modules: dict[str, list[str]] = {}

    def process_files(self) -> None:
        """Processes each Python file found in the specified directory.

        For each Python file, this method updates the directory_modules with the file's information, parses the file, and saves the parsed data as JSON.

        Example:
            >>> vm.process_files()
            # Processes all Python files and saves their parsed data.
        """
        python_files: list[str] = self._get_python_files()
        for file in python_files:
            self._process_file(file)

    @logging_decorator(message="Saving visited directories")
    def save_visited_directories(self) -> None:
        """
        Saves a JSON file mapping each visited directory to its Python files.

        The output is saved in a file named '00_directory_module_map.json' within the specified output directory.

        Example:
            >>> vm.save_visited_directories()
            # Saves a mapping of directories to Python files as JSON.
        """
        output_path: str = self._get_directory_map_output_path()
        self._write_json_directory_map(output_path)

    def _create_output_directory(self) -> None:
        """Creates the output directory if it does not already exist."""
        os.makedirs(self.output_directory, exist_ok=True)

    def _walk_directories(self) -> list[str]:
        all_files: list[str] = []
        for root, directories, files in os.walk(self.directory):
            directories[:] = [
                directory
                for directory in directories
                if directory not in EXCLUDED_DIRECTORIES
            ]
            all_files.extend(os.path.join(root, file) for file in files)
        return all_files

    def _filter_python_files(self, files: list[str]) -> list[str]:
        """Filters a list of files to only include Python files."""
        return [file for file in files if file.endswith(".py")]

    @logging_decorator(message="Getting Python files")
    def _get_python_files(self) -> list[str]:
        """Gets all Python files in the specified directory."""
        all_files: list[str] = self._walk_directories()
        return self._filter_python_files(all_files)

    def _process_file(self, file_path: str) -> None:
        """Processes a single Python file."""
        root: str = os.path.dirname(file_path)
        self.directory_modules.setdefault(root, []).append(os.path.basename(file_path))
        self._parse_and_save_file(file_path)

    @logging_decorator(message="Processing file")
    def _parse_and_save_file(self, file_path: str) -> None:
        """Parses a Python file and saves the parsed data as JSON."""
        parser = PythonParser(file_path)
        code: str = parser.open_file()
        module_model: ModuleModel | None = parser.parse(code)
        if module_model:
            self._save_model_as_json(module_model, file_path)

    @logging_decorator(message="Saving model as JSON")
    def _save_model_as_json(self, module_model: ModuleModel, file_path: str) -> None:
        """Saves a parsed ModuleModel as JSON."""
        json_output_directory: str = self._create_json_output_directory()
        output_path: str = self._get_json_output_path(file_path, json_output_directory)
        self._write_json_file(module_model, output_path)

    def _create_json_output_directory(self) -> str:
        """Creates the JSON output directory if it does not already exist."""
        json_output_directory: str = os.path.join(self.output_directory, "json")
        os.makedirs(json_output_directory, exist_ok=True)
        return json_output_directory

    def _get_json_output_path(self, file_path: str, json_output_directory: str) -> str:
        """Gets the output path for a JSON file."""
        relative_path: str = os.path.relpath(file_path, self.directory)
        safe_relative_path: str = relative_path.replace(os.sep, ":").rstrip(".py")
        return os.path.join(json_output_directory, f"{safe_relative_path}.json")

    def _write_json_file(self, module_model: ModuleModel, output_path: str) -> None:
        """Writes a JSON file containing the parsed data from a ModuleModel."""
        parsed_data_json: str = module_model.model_dump_json(indent=4)
        with open(output_path, "w") as json_file:
            json_file.write(parsed_data_json)

    def _get_directory_map_output_path(self) -> str:
        """Gets the output path for the directory map JSON file."""
        return os.path.join(self.output_directory, "00_directory_module_map.json")

    def _write_json_directory_map(self, output_path: str) -> None:
        """Writes the directory map JSON file."""
        with open(output_path, "w") as json_file:
            json.dump(self.directory_modules, json_file, indent=4)
