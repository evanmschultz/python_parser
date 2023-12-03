from models.models import BaseCodeBlockModel, ModuleModel
from parsers.python_parser import PythonParser


def main() -> None:
    """
    Main function that parses a Python file and saves the parsed data to a JSON file.

    Returns:
        None
    """
    parser = PythonParser("./sample_file.py")
    code: str = parser.open_file()
    module_model: ModuleModel | None = parser.parse(code)

    # Ensure module_model is an instance of ModuleModel or BaseCodeBlockModel
    if isinstance(module_model, ModuleModel):
        parsed_data_json: str = module_model.model_dump_json(indent=4)
        json_file_name: str = "Output.json"

        # Save the parsed data to sample_output.json
        with open(json_file_name, "w") as outfile:
            outfile.write(parsed_data_json)

        print(f"Parsed data saved to: {json_file_name}")
    else:
        print("Error: The parsed model is not of the expected type.")


if __name__ == "__main__":
    main()
