import json
import os
from logger.decorators import logging_decorator

from parsers.python_parser import PythonParser
from models.models import ModuleModel

EXCLUDED_DIRECTORIES: set[str] = {".venv", "node_modules", "__pycache__", ".git"}


class VisitorManager:
    @logging_decorator(message="Initializing VisitorManager")
    def __init__(self, directory: str, output_directory: str = "output") -> None:
        self.directory: str = directory
        self.output_directory: str = output_directory
        self._create_output_directory()
        self.directory_modules: dict[str, list[str]] = {}

    def _create_output_directory(self) -> None:
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
        return [file for file in files if file.endswith(".py")]

    @logging_decorator(message="Getting Python files")
    def get_python_files(self) -> list[str]:
        all_files: list[str] = self._walk_directories()
        return self._filter_python_files(all_files)

    def process_files(self) -> None:
        python_files: list[str] = self.get_python_files()
        for file in python_files:
            self._process_file(file)

    def _process_file(self, file_path: str) -> None:
        root: str = os.path.dirname(file_path)
        self.directory_modules.setdefault(root, []).append(os.path.basename(file_path))
        self._parse_and_save_file(file_path)

    @logging_decorator(message="Processing file")
    def _parse_and_save_file(self, file_path: str) -> None:
        parser = PythonParser(file_path)
        code: str = parser.open_file()
        module_model: ModuleModel | None = parser.parse(code)
        if module_model:
            self._save_model_as_json(module_model, file_path)

    @logging_decorator(message="Saving model as JSON")
    def _save_model_as_json(self, module_model: ModuleModel, file_path: str) -> None:
        json_output_directory: str = self._create_json_output_directory()
        output_path: str = self._get_json_output_path(file_path, json_output_directory)
        self._write_json_file(module_model, output_path)

    def _create_json_output_directory(self) -> str:
        json_output_directory: str = os.path.join(self.output_directory, "json")
        os.makedirs(json_output_directory, exist_ok=True)
        return json_output_directory

    def _get_json_output_path(self, file_path: str, json_output_directory: str) -> str:
        relative_path: str = os.path.relpath(file_path, self.directory)
        safe_relative_path: str = relative_path.replace(os.sep, ":").strip(".py")
        return os.path.join(json_output_directory, f"{safe_relative_path}.json")

    def _write_json_file(self, module_model: ModuleModel, output_path: str) -> None:
        parsed_data_json: str = module_model.model_dump_json(indent=4)
        with open(output_path, "w") as json_file:
            json_file.write(parsed_data_json)

    @logging_decorator(message="Saving visited directories")
    def save_visited_directories(self) -> None:
        output_path: str = self._get_directory_map_output_path()
        self._write_json_directory_map(output_path)

    def _get_directory_map_output_path(self) -> str:
        return os.path.join(self.output_directory, "00_directory_module_map.json")

    def _write_json_directory_map(self, output_path: str) -> None:
        with open(output_path, "w") as json_file:
            json.dump(self.directory_modules, json_file, indent=4)
